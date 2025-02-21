import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Navbar({ user }) {
  return (
    <nav className="w-full bg-white border-b border-gray-200">
      {/* Full-width container with proper spacing */}
      <div className="w-full px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
        {/* Left-aligned logo and brand */}
        <div className="flex items-center">
          <img src="/mic.jpg" alt="Logo" className="h-8 w-auto mr-2" />
          <span className="text-xl font-bold">AskPod</span>
        </div>

        {/* Right-aligned user info and logout button */}
        <div className="flex items-center justify-end flex-1 space-x-4">
          <span className="text-gray-700">Hello, {user.username}</span>
          <Button variant="outline" size="sm" asChild>
            <Link href="/logout">Logout</Link>
          </Button>
        </div>
      </div>
    </nav>
  );
}