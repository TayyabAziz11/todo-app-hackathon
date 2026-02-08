# Dapr SDK Examples - Multi-Language Reference

Complete examples for using Dapr SDKs across different programming languages.

## Table of Contents

1. [Installation](#installation)
2. [Python Examples](#python-examples)
3. [Go Examples](#go-examples)
4. [JavaScript/TypeScript Examples](#javascripttypescript-examples)
5. [Java Examples](#java-examples)
6. [.NET Examples](#net-examples)

---

## Installation

### Python
```bash
pip install dapr dapr-ext-grpc dapr-ext-workflow
```

### Go
```bash
go get github.com/dapr/go-sdk
```

### JavaScript/TypeScript
```bash
npm install @dapr/dapr
```

### Java
```xml
<dependency>
    <groupId>io.dapr</groupId>
    <artifactId>dapr-sdk</artifactId>
    <version>1.11.0</version>
</dependency>
```

### .NET
```bash
dotnet add package Dapr.Client
dotnet add package Dapr.AspNetCore
```

---

## Python Examples

### Service Invocation

```python
from dapr.clients import DaprClient

# HTTP invocation
with DaprClient() as client:
    # GET request
    resp = client.invoke_method(
        app_id='checkout-service',
        method_name='get-order',
        data='{"orderId": 123}',
        http_verb='GET'
    )
    print(resp.text())

    # POST request
    resp = client.invoke_method(
        app_id='checkout-service',
        method_name='create-order',
        data='{"item": "book", "quantity": 1}',
        http_verb='POST',
        content_type='application/json'
    )
```

### State Management

```python
from dapr.clients import DaprClient
import json

with DaprClient() as client:
    store_name = 'statestore'

    # Save state
    client.save_state(
        store_name=store_name,
        key='user-123',
        value=json.dumps({'name': 'Alice', 'email': 'alice@example.com'}),
        state_metadata={'ttlInSeconds': '3600'}
    )

    # Get state
    state = client.get_state(store_name=store_name, key='user-123')
    if state.data:
        user = json.loads(state.data)
        print(f"User: {user}")

    # Get bulk state
    states = client.get_bulk_state(
        store_name=store_name,
        keys=['user-123', 'user-456']
    ).items
    for item in states:
        print(f"{item.key}: {item.data}")

    # Delete state
    client.delete_state(store_name=store_name, key='user-123')

    # State transaction
    client.execute_state_transaction(
        store_name=store_name,
        operations=[
            {
                'operation': 'upsert',
                'request': {
                    'key': 'user-789',
                    'value': json.dumps({'name': 'Bob'})
                }
            },
            {
                'operation': 'delete',
                'request': {'key': 'user-123'}
            }
        ]
    )
```

### Pub/Sub

**Publisher:**
```python
from dapr.clients import DaprClient
import json

with DaprClient() as client:
    order = {'orderId': 123, 'amount': 99.99}

    client.publish_event(
        pubsub_name='orderpubsub',
        topic_name='orders',
        data=json.dumps(order),
        data_content_type='application/json',
        metadata={'priority': 'high'}
    )
    print("Event published")
```

**Subscriber (Flask):**
```python
from flask import Flask, request
from cloudevents.http import from_http
import json

app = Flask(__name__)

@app.route('/dapr/subscribe', methods=['GET'])
def subscribe():
    return json.dumps([{
        'pubsubname': 'orderpubsub',
        'topic': 'orders',
        'route': '/orders'
    }])

@app.route('/orders', methods=['POST'])
def orders_subscriber():
    event = from_http(request.headers, request.get_data())
    data = json.loads(event.data)
    print(f"Received order: {data['orderId']}")
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}

if __name__ == '__main__':
    app.run(port=5000)
```

### Bindings

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    # Output binding (send to Kafka)
    resp = client.invoke_binding(
        binding_name='kafka-binding',
        operation='create',
        data='{"message": "Hello Kafka"}',
        binding_metadata={'topic': 'orders'}
    )

    # Input binding handler (Flask route)
    @app.route('/kafka-binding', methods=['POST'])
    def kafka_input():
        data = request.json
        print(f"Received: {data}")
        return {}, 200
```

### Secrets

```python
from dapr.clients import DaprClient

with DaprClient() as client:
    # Get secret
    secret = client.get_secret(
        store_name='kubernetes-secrets',
        key='db-password'
    )
    password = secret.secret['db-password']

    # Get bulk secrets
    secrets = client.get_bulk_secret(store_name='vault')
    for key, value in secrets.secrets.items():
        print(f"{key}: {value}")
```

---

## Go Examples

### Service Invocation

```go
package main

import (
    "context"
    "fmt"
    "log"

    dapr "github.com/dapr/go-sdk/client"
)

func main() {
    ctx := context.Background()
    client, err := dapr.NewClient()
    if err != nil {
        log.Fatal(err)
    }
    defer client.Close()

    // Invoke method
    resp, err := client.InvokeMethod(ctx, "checkout-service", "create-order", "post")
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("Response: %s\n", string(resp))

    // With content
    content := &dapr.DataContent{
        ContentType: "application/json",
        Data:        []byte(`{"orderId": 123}`),
    }
    resp, err = client.InvokeMethodWithContent(ctx, "checkout-service", "process-order", "post", content)
}
```

### State Management

```go
package main

import (
    "context"
    "encoding/json"
    "fmt"
    "log"

    dapr "github.com/dapr/go-sdk/client"
)

type Order struct {
    OrderID int    `json:"orderId"`
    Amount  float64 `json:"amount"`
}

func main() {
    ctx := context.Background()
    client, err := dapr.NewClient()
    if err != nil {
        log.Fatal(err)
    }
    defer client.Close()

    storeName := "statestore"

    // Save state
    order := Order{OrderID: 123, Amount: 99.99}
    data, _ := json.Marshal(order)

    if err := client.SaveState(ctx, storeName, "order-123", data, nil); err != nil {
        log.Fatal(err)
    }

    // Get state
    item, err := client.GetState(ctx, storeName, "order-123", nil)
    if err != nil {
        log.Fatal(err)
    }

    var retrieved Order
    json.Unmarshal(item.Value, &retrieved)
    fmt.Printf("Order: %+v\n", retrieved)

    // Save with ETag
    err = client.SaveState(ctx, storeName, "order-123", data, map[string]string{
        "concurrency": "first-write",
        "consistency": "strong",
    }, &dapr.SetStateOption{
        Etag: &item.Etag,
    })

    // Transaction
    ops := []*dapr.StateOperation{
        {
            Type: dapr.StateOperationTypeUpsert,
            Item: &dapr.SetStateItem{
                Key:   "key1",
                Value: []byte("value1"),
            },
        },
        {
            Type: dapr.StateOperationTypeDelete,
            Item: &dapr.SetStateItem{
                Key: "key2",
            },
        },
    }

    if err := client.ExecuteStateTransaction(ctx, storeName, nil, ops); err != nil {
        log.Fatal(err)
    }
}
```

### Pub/Sub

**Publisher:**
```go
package main

import (
    "context"
    "log"

    dapr "github.com/dapr/go-sdk/client"
)

func main() {
    ctx := context.Background()
    client, err := dapr.NewClient()
    if err != nil {
        log.Fatal(err)
    }
    defer client.Close()

    data := []byte(`{"orderId": 123}`)

    if err := client.PublishEvent(ctx, "orderpubsub", "orders", data); err != nil {
        log.Fatal(err)
    }

    // With metadata
    if err := client.PublishEventWithMetadata(ctx, "orderpubsub", "orders", data,
        map[string]string{"priority": "high"}); err != nil {
        log.Fatal(err)
    }
}
```

**Subscriber (HTTP Server):**
```go
package main

import (
    "encoding/json"
    "log"
    "net/http"

    "github.com/dapr/go-sdk/service/common"
    daprd "github.com/dapr/go-sdk/service/http"
)

type Order struct {
    OrderID int `json:"orderId"`
}

func main() {
    s := daprd.NewService(":6000")

    // Subscribe
    if err := s.AddTopicEventHandler(&common.Subscription{
        PubsubName: "orderpubsub",
        Topic:      "orders",
        Route:      "/orders",
    }, orderHandler); err != nil {
        log.Fatal(err)
    }

    if err := s.Start(); err != nil && err != http.ErrServerClosed {
        log.Fatal(err)
    }
}

func orderHandler(ctx context.Context, e *common.TopicEvent) (retry bool, err error) {
    var order Order
    if err := json.Unmarshal(e.RawData, &order); err != nil {
        return false, err
    }

    log.Printf("Received order: %d", order.OrderID)
    return false, nil
}
```

### Bindings

```go
package main

import (
    "context"
    "log"

    dapr "github.com/dapr/go-sdk/client"
)

func main() {
    ctx := context.Background()
    client, err := dapr.NewClient()
    if err != nil {
        log.Fatal(err)
    }
    defer client.Close()

    // Output binding
    req := &dapr.InvokeBindingRequest{
        Name:      "kafka-binding",
        Operation: "create",
        Data:      []byte(`{"message": "Hello"}`),
        Metadata:  map[string]string{"topic": "orders"},
    }

    if err := client.InvokeOutputBinding(ctx, req); err != nil {
        log.Fatal(err)
    }
}
```

---

## JavaScript/TypeScript Examples

### Service Invocation

```typescript
import { DaprClient, HttpMethod } from "@dapr/dapr";

const client = new DaprClient({ daprHost: "127.0.0.1", daprPort: "3500" });

async function invokeService() {
    // GET request
    const response = await client.invoker.invoke(
        "checkout-service",
        "get-order",
        HttpMethod.GET,
        { orderId: 123 }
    );
    console.log(response);

    // POST request
    const createResp = await client.invoker.invoke(
        "checkout-service",
        "create-order",
        HttpMethod.POST,
        { item: "book", quantity: 1 }
    );
}

invokeService();
```

### State Management

```typescript
import { DaprClient } from "@dapr/dapr";

const client = new DaprClient();
const stateStore = "statestore";

async function stateOperations() {
    // Save state
    await client.state.save(stateStore, [
        { key: "user-123", value: { name: "Alice", email: "alice@example.com" } }
    ]);

    // Get state
    const user = await client.state.get(stateStore, "user-123");
    console.log(user);

    // Get bulk
    const items = await client.state.getBulk(stateStore, ["user-123", "user-456"]);
    items.forEach(item => console.log(`${item.key}: ${item.value}`));

    // Delete
    await client.state.delete(stateStore, "user-123");

    // Transaction
    await client.state.transaction(stateStore, [
        { operation: "upsert", request: { key: "key1", value: "value1" } },
        { operation: "delete", request: { key: "key2" } }
    ]);

    // With ETag
    const stateWithEtag = await client.state.get(stateStore, "order-123");
    await client.state.save(stateStore, [
        {
            key: "order-123",
            value: { status: "updated" },
            etag: stateWithEtag.etag
        }
    ]);
}

stateOperations();
```

### Pub/Sub

**Publisher:**
```typescript
import { DaprClient } from "@dapr/dapr";

const client = new DaprClient();

async function publishEvent() {
    const order = { orderId: 123, amount: 99.99 };

    await client.pubsub.publish("orderpubsub", "orders", order);
    console.log("Event published");
}

publishEvent();
```

**Subscriber (Express):**
```typescript
import { DaprServer } from "@dapr/dapr";
import express from "express";

const app = express();
const daprServer = new DaprServer({ serverHost: "127.0.0.1", serverPort: "5000" });

// Subscribe
await daprServer.pubsub.subscribe("orderpubsub", "orders", async (data: any) => {
    console.log(`Received order: ${data.orderId}`);
});

await daprServer.start();
```

---

## Java Examples

### Service Invocation

```java
import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;

public class ServiceInvocation {
    public static void main(String[] args) {
        try (DaprClient client = new DaprClientBuilder().build()) {
            // Invoke method
            byte[] response = client.invokeMethod(
                "checkout-service",
                "create-order",
                "{\"orderId\": 123}".getBytes(),
                io.dapr.client.domain.HttpExtension.POST
            ).block();

            System.out.println("Response: " + new String(response));
        }
    }
}
```

### State Management

```java
import io.dapr.client.DaprClient;
import io.dapr.client.DaprClientBuilder;
import io.dapr.client.domain.State;

public class StateExample {
    public static void main(String[] args) {
        try (DaprClient client = new DaprClientBuilder().build()) {
            String storeName = "statestore";

            // Save state
            client.saveState(storeName, "order-123",
                "{\"orderId\": 123, \"amount\": 99.99}").block();

            // Get state
            State<String> state = client.getState(storeName, "order-123", String.class).block();
            System.out.println("Order: " + state.getValue());

            // Delete state
            client.deleteState(storeName, "order-123").block();
        }
    }
}
```

---

## .NET Examples

### Service Invocation

```csharp
using Dapr.Client;

var client = new DaprClientBuilder().Build();

// Invoke method
var order = new { orderId = 123, amount = 99.99 };
var response = await client.InvokeMethodAsync<object, string>(
    "checkout-service",
    "create-order",
    order,
    HttpInvocationOptions.HttpMethodPost
);

Console.WriteLine($"Response: {response}");
```

### State Management

```csharp
using Dapr.Client;

var client = new DaprClientBuilder().Build();
var storeName = "statestore";

// Save state
var order = new Order { OrderId = 123, Amount = 99.99 };
await client.SaveStateAsync(storeName, "order-123", order);

// Get state
var retrieved = await client.GetStateAsync<Order>(storeName, "order-123");
Console.WriteLine($"Order: {retrieved.OrderId}");

// Delete state
await client.DeleteStateAsync(storeName, "order-123");

// Transaction
var operations = new List<StateTransactionRequest>
{
    new StateTransactionRequest("key1", JsonSerializer.SerializeToUtf8Bytes("value1"), StateOperationType.Upsert),
    new StateTransactionRequest("key2", null, StateOperationType.Delete)
};

await client.ExecuteStateTransactionAsync(storeName, operations);
```

### Pub/Sub (ASP.NET Core)

```csharp
using Dapr;
using Microsoft.AspNetCore.Mvc;

var builder = WebApplication.CreateBuilder(args);
builder.Services.AddControllers().AddDapr();

var app = builder.Build();
app.MapSubscribeHandler();

// Subscribe endpoint
[Topic("orderpubsub", "orders")]
[HttpPost("/orders")]
public async Task<IActionResult> ProcessOrder([FromBody] Order order)
{
    Console.WriteLine($"Received order: {order.OrderId}");
    return Ok();
}

app.Run();
```

**Publisher:**
```csharp
var client = new DaprClientBuilder().Build();
var order = new Order { OrderId = 123, Amount = 99.99 };

await client.PublishEventAsync("orderpubsub", "orders", order);
```
