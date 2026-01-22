import type { Metadata } from 'next';
import './globals.css';
import { AuthProvider } from '@/lib/auth';
import FloatingChatbot from '@/components/FloatingChatbot';

export const metadata: Metadata = {
  title: 'Todo App - AI-Powered Task Management',
  description: 'Manage your tasks using natural language with our AI-powered chatbot assistant',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">
        <AuthProvider>
          {children}
          <FloatingChatbot />
        </AuthProvider>
      </body>
    </html>
  );
}
