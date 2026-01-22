/**
 * Chat Page
 *
 * Main page for the Todo AI Chatbot.
 * Renders the ChatInterface component with authentication guard.
 * Redirects to login if user is not authenticated.
 */

"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/lib/auth";
import ChatInterface from "@/components/ChatInterface";

export default function ChatPage() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  // Redirect to login if not authenticated
  useEffect(() => {
    if (!isLoading && !user) {
      router.push("/login");
    }
  }, [user, isLoading, router]);

  // Show loading state while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  // Show nothing if not authenticated (will redirect)
  if (!user) {
    return null;
  }

  // Render chat interface for authenticated users
  return <ChatInterface />;
}
