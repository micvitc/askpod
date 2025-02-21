"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { useRouter } from "next/router";

export default function NewSession({ onSessionCreated }) {
  const router = useRouter();

  const createSession = async () => {
    try {
      const res = await fetch("/api/create-session", {
        method: "POST",
        credentials: "include",
      });

      if (!res.ok) {
        alert("Failed to create session");
        return;
      }
      const data = await res.json();
      onSessionCreated && onSessionCreated(data);
      router.push(`/session/${data.id}`);
    } catch (error) {
      console.error("Error creating session:", error);
    }
  };

  return (
    <div className="my-4">
      <Button onClick={createSession}>Create New Session</Button>
    </div>
  );
}