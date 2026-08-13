import React from "react";

export const MainLayout = ({ sidebar, main }: { sidebar: React.ReactNode; main: React.ReactNode }) => {
  return (
    <div className="flex h-screen w-full bg-sahistra-bg overflow-hidden">
      {/* Sidebar - hidden on small screens unless toggled */}
      <div className="hidden md:flex w-64 flex-col border-r border-sahistra-text/5 bg-sahistra-bg">
        {sidebar}
      </div>
      
      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0 relative">
        {main}
      </div>
    </div>
  );
};
