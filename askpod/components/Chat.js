"use client";

import React, { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState("");

  const handleSend = () => {
    if (!inputValue.trim()) return;
    // For now, simply add the message locally.
    setMessages([...messages, { sender: "user", text: inputValue }]);
    setInputValue("");
  };

  return (
    <Card className="flex flex-col h-full">
      <CardHeader>
        <CardTitle>Chat</CardTitle>
        <CardDescription>Chat with our assistant.</CardDescription>
      </CardHeader>
      <CardContent className="flex-grow overflow-y-auto p-4 space-y-2">
        {messages.length === 0 ? (
          <p className="text-gray-500">No messages yet. Start the conversation!</p>
        ) : (
          messages.map((msg, index) => (
            <div
              key={index}
              className={`p-2 rounded ${
                msg.sender === "user" ? "bg-blue-100 text-right" : "bg-gray-100 text-left"
              }`}
            >
              {msg.text}
            </div>
          ))
        )}
      </CardContent>
      <div className="p-4 border-t flex gap-2">
        <Input
          className="flex-1"
          placeholder="Type your message..."
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
        />
        <Button onClick={handleSend}>Send</Button>
      </div>
    </Card>
  );
}