"use client";

import { ChangeEvent, useState, KeyboardEvent, useRef } from "react";

import "./index.css";

type Message = {
    id: number;
    text: string;
    sender: "user" | "gemini";
};

export default function Home() {
    const chatRef = useRef<HTMLDivElement>(null);

    const [messages, setMessages] = useState<Message[]>([]);
    const [input, setInput] = useState<string>("");

    const handleInputChange = (event: ChangeEvent<HTMLInputElement>) => {
        setInput(event.target.value);
    };

    const handleKeyDown = (event: KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            handleSendMessage();
        }
    };

    const handleSendMessage = async () => {
        const userMessage: Message = {
            id: Date.now() + 1,
            text: input,
            sender: "user",
        };

        const geminiMessageID = Date.now();

        const geminiMessage: Message = {
            id: geminiMessageID,
            text: "",
            sender: "gemini",
        };

        setMessages((prevMessages) => [
            geminiMessage,
            userMessage,
            ...prevMessages,
        ]);

        setInput("");

        try {
            const response = await fetch("http://127.0.0.1:5000/chat", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    user_prompt: input,
                }),
            });

            if (!response.body) {
                throw new Error("Stream failed to start");
            }

            const reader = response.body.getReader();
            const decoder = new TextDecoder();

            let receivedText = "";

            while (true) {
                const { value, done } = await reader.read();

                if (done) break;

                const chunk = decoder.decode(value);

                receivedText += chunk;

                setMessages((prevMessages) => {
                    const messageIndex = prevMessages.findIndex(
                        (m) => m.id === geminiMessageID,
                    );

                    if (messageIndex === -1) {
                        console.warn("Gemini not found");

                        return prevMessages;
                    }

                    const newMessages = [...prevMessages];

                    newMessages[messageIndex] = {
                        ...newMessages[messageIndex],
                        text: receivedText,
                    };

                    return newMessages;
                });
            }
        } catch (error) {
            setMessages((prevMessages) => {
                const messageIndex = prevMessages.findIndex(
                    (m) => m.id === geminiMessageID,
                );

                if (messageIndex === -1) {
                    console.warn("Gemini not found");

                    return prevMessages;
                }

                const newMessages = [...prevMessages];

                newMessages[messageIndex] = {
                    ...newMessages[messageIndex],
                    text: `ERROR: ${error}`,
                };

                return newMessages;
            });
        }
    };

    return (
        <div className="gemini-wrapper" ref={chatRef}>
            <div className={`chat ${messages.length == 0 ? "r" : ""}`}>
                {messages.map((message, index) => (
                    <div key={index} className={`m ${message.sender}`}>
                        {message.text}
                    </div>
                ))}
            </div>
            <div className="chat-area r">
                <input
                    type="text"
                    id="chat-box"
                    className="chat-box"
                    placeholder="Ask anything..."
                    value={input}
                    onChange={handleInputChange}
                    onKeyDown={handleKeyDown}
                />
            </div>
        </div>
    );
}
