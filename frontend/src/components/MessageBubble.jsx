import React from "react";

const roleConfig = {
  user:      { bg: "bg-blue-600",  align: "justify-end",   label: "Vous" },
  assistant: { bg: "bg-gray-700",  align: "justify-start", label: "🩺 MedAssist" },
  system:    { bg: "bg-yellow-600",align: "justify-start", label: "Système" },
};

export default function MessageBubble({ role, content, isStreaming }) {
  const { bg, align, label } = roleConfig[role] || roleConfig.assistant;

  return (
    <div className={`flex ${align} mb-4`}>
      <div className={`max-w-[75%] rounded-2xl px-4 py-3 text-white ${bg} shadow-lg`}>
        <div className="text-xs font-semibold opacity-60 mb-1">{label}</div>
        <div className="whitespace-pre-wrap text-sm leading-relaxed">
          {content}
          {isStreaming && <span className="inline-block w-2 h-4 bg-white ml-1 animate-pulse rounded" />}
        </div>
      </div>
    </div>
  );
}
