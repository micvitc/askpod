import Link from "next/link";
import { Button } from "@/components/ui/button"; // Adjust path if needed

export default function Navbar({ user }) {
  return (
    <nav className="w-full bg-white border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex items-center justify-between h-16">
        <div className="flex items-center">
          <span className="text-xl font-bold">AskPod</span>
        </div>
        <div className="flex items-center space-x-4">
          <span className="text-gray-700">Hello, {user.username}</span>
          <Button variant="outline" size="sm" asChild>
            <Link href="/logout">Logout</Link>
          </Button>
        </div>
      </div>
    </nav>
  );
}