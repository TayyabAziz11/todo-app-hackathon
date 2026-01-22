"use client";

/**
 * FloatingChatbot Component
 *
 * A floating AI chatbot launcher that appears in the bottom-right corner.
 * Provides quick access to the AI Chat interface with authentication awareness.
 *
 * Features:
 * - Fixed position bottom-right corner
 * - Greeting message for authenticated users (auto-dismisses)
 * - Click to navigate to /chat (authenticated) or /login (unauthenticated)
 * - Friendly robot icon with subtle animations
 * - Respects authentication rules
 */

import { useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";
import { useAuth } from "@/lib/auth";

export default function FloatingChatbot() {
  const { user, isLoading } = useAuth();
  const router = useRouter();
  const pathname = usePathname();
  const [showGreeting, setShowGreeting] = useState(false);
  const [greetingDismissed, setGreetingDismissed] = useState(false);

  // Show greeting for authenticated users (once per session)
  useEffect(() => {
    if (!isLoading && user && !greetingDismissed) {
      // Check if greeting was already shown this session
      const greetingShown = sessionStorage.getItem("chatbot_greeting_shown");
      if (!greetingShown) {
        // Show greeting after a short delay
        const timer = setTimeout(() => {
          setShowGreeting(true);
          sessionStorage.setItem("chatbot_greeting_shown", "true");
        }, 1500);

        return () => clearTimeout(timer);
      }
    }
  }, [user, isLoading, greetingDismissed]);

  // Auto-dismiss greeting after 8 seconds
  useEffect(() => {
    if (showGreeting) {
      const timer = setTimeout(() => {
        setShowGreeting(false);
      }, 8000);

      return () => clearTimeout(timer);
    }
  }, [showGreeting]);

  // Handle chatbot click
  const handleClick = () => {
    if (!user) {
      // Not authenticated - redirect to login
      router.push("/login");
    } else {
      // Authenticated - navigate to chat
      router.push("/chat");
    }
  };

  // Dismiss greeting manually
  const dismissGreeting = () => {
    setShowGreeting(false);
    setGreetingDismissed(true);
  };

  // Don't show on login/register pages or if already on chat page
  if (pathname === "/login" || pathname === "/register" || pathname === "/chat") {
    return null;
  }

  return (
    <>
      {/* Greeting Bubble */}
      {showGreeting && user && (
        <div
          className="fixed bottom-28 right-6 z-50 animate-fade-in-up"
          role="alert"
          aria-live="polite"
        >
          <div className="relative bg-white rounded-2xl shadow-2xl border border-gray-100 p-4 max-w-xs">
            {/* Close button */}
            <button
              onClick={dismissGreeting}
              className="absolute top-2 right-2 text-gray-400 hover:text-gray-600 transition-colors"
              aria-label="Dismiss greeting"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            {/* Greeting content */}
            <div className="flex items-start gap-3 pr-4">
              <div className="flex-shrink-0 w-10 h-10 bg-gradient-to-br from-indigo-500 to-purple-600 rounded-full flex items-center justify-center">
                <span className="text-xl">🤖</span>
              </div>
              <div>
                <p className="font-semibold text-gray-900 mb-1">
                  Hi {user.name || "there"}! 👋
                </p>
                <p className="text-sm text-gray-600">
                  I'm your AI Todo Assistant. Need help managing tasks?
                </p>
              </div>
            </div>

            {/* Speech bubble tail */}
            <div className="absolute bottom-0 right-8 transform translate-y-1/2 rotate-45 w-3 h-3 bg-white border-r border-b border-gray-100"></div>
          </div>
        </div>
      )}

      {/* Floating Chatbot Button */}
      <button
        onClick={handleClick}
        className="fixed bottom-6 right-6 z-50 w-16 h-16 bg-gradient-to-br from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white rounded-full shadow-2xl hover:shadow-indigo-500/50 transition-all hover:scale-110 active:scale-95 flex items-center justify-center group animate-bounce-gentle"
        aria-label={user ? "Open AI Chat" : "Sign in to chat"}
      >
        {/* Robot Icon */}
        <svg
          className="w-8 h-8 group-hover:scale-110 transition-transform"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z"
          />
        </svg>

        {/* Pulse animation indicator */}
        <span className="absolute inset-0 rounded-full bg-indigo-400 opacity-75 animate-ping"></span>
      </button>

      {/* Custom animations */}
      <style jsx>{`
        @keyframes fade-in-up {
          from {
            opacity: 0;
            transform: translateY(10px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }

        @keyframes bounce-gentle {
          0%, 100% {
            transform: translateY(0);
          }
          50% {
            transform: translateY(-5px);
          }
        }

        .animate-fade-in-up {
          animation: fade-in-up 0.4s ease-out;
        }

        .animate-bounce-gentle {
          animation: bounce-gentle 3s ease-in-out infinite;
        }
      `}</style>
    </>
  );
}
