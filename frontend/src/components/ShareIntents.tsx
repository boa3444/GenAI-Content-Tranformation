"use client";

import React, { useState } from "react";
import { Share2, Twitter, Linkedin, Check, Copy } from "lucide-react";

interface ShareIntentsProps {
  title?: string;
  text: string;
  url?: string;
  hashtags?: string[];
  platform?: "twitter" | "linkedin" | "generic";
}

export const ShareIntents: React.FC<ShareIntentsProps> = ({
  title = "AI Transformation Intelligence",
  text,
  url = typeof window !== "undefined" ? window.location.href : "https://ai-transformation.engine",
  hashtags = ["AI", "ContentTransformation", "Automation"],
  platform = "generic"
}) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const handleNativeShare = async () => {
    if (navigator.share) {
      try {
        await navigator.share({
          title,
          text,
          url
        });
      } catch (err) {
        console.log("Share cancelled or failed:", err);
      }
    } else {
      handleCopy();
    }
  };

  const handleTwitterShare = () => {
    const encodedText = encodeURIComponent(text);
    const encodedHashtags = encodeURIComponent(hashtags.join(","));
    const twitterUrl = `https://twitter.com/intent/tweet?text=${encodedText}&hashtags=${encodedHashtags}`;
    window.open(twitterUrl, "_blank", "width=600,height=400,noopener,noreferrer");
  };

  const handleLinkedInShare = () => {
    const shareUrl = encodeURIComponent(url);
    const linkedinUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${shareUrl}`;
    window.open(linkedinUrl, "_blank", "width=600,height=600,noopener,noreferrer");
  };

  return (
    <div className="flex flex-wrap items-center gap-2 mt-4 pt-4 border-t border-gray-100">
      <button
        onClick={handleCopy}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-gray-200 text-xs font-medium text-gray-700 hover:bg-gray-50 hover:border-gray-300 transition-all shadow-sm"
      >
        {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-blue-600" />}
        {copied ? "Copied to Clipboard" : "Copy Content"}
      </button>

      <button
        onClick={handleTwitterShare}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-sky-50 border border-sky-200 text-xs font-medium text-sky-700 hover:bg-sky-100 transition-all shadow-sm"
      >
        <Twitter className="w-3.5 h-3.5 text-sky-500" />
        Post to X / Twitter
      </button>

      <button
        onClick={handleLinkedInShare}
        className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-blue-50 border border-blue-200 text-xs font-medium text-blue-700 hover:bg-blue-100 transition-all shadow-sm"
      >
        <Linkedin className="w-3.5 h-3.5 text-blue-600" />
        Share on LinkedIn
      </button>

      {typeof navigator !== "undefined" && "share" in navigator && (
        <button
          onClick={handleNativeShare}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-white border border-gray-200 text-xs font-medium text-gray-700 hover:bg-gray-50 transition-all shadow-sm"
        >
          <Share2 className="w-3.5 h-3.5 text-indigo-600" />
          Native Share
        </button>
      )}
    </div>
  );
};
