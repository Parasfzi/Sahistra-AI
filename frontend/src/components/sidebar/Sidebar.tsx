
import { Settings, Plus, MessageSquare } from "lucide-react";

export const Sidebar = () => {
  return (
    <div className="flex flex-col h-full p-4">
      <div className="mb-8">
        <h1 className="text-2xl font-serif font-semibold tracking-wide">Sahistra</h1>
      </div>
      
      <button className="flex items-center gap-2 px-4 py-2 bg-sahistra-text text-sahistra-bg rounded-md hover:bg-sahistra-text/90 transition-colors mb-6 text-sm font-medium">
        <Plus size={16} />
        New Conversation
      </button>

      <div className="flex-1 overflow-y-auto pr-2">
        <div className="mb-6">
          <h3 className="text-xs font-semibold text-sahistra-text/50 uppercase tracking-wider mb-3">Today</h3>
          <div className="space-y-1">
            <button className="w-full text-left flex items-center gap-2 px-3 py-2 bg-sahistra-card rounded-md text-sm">
              <MessageSquare size={14} className="text-sahistra-text/70" />
              <span className="truncate">Active Conversation</span>
            </button>
          </div>
        </div>
      </div>

      <div className="mt-auto pt-4 border-t border-sahistra-text/5 space-y-1">
        <button className="w-full text-left flex items-center gap-2 px-3 py-2 hover:bg-sahistra-card rounded-md text-sm text-sahistra-text/80 transition-colors">
          <Settings size={16} />
          Settings
        </button>
      </div>
    </div>
  );
};
