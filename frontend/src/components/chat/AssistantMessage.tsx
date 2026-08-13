import ReactMarkdown from "react-markdown";

export const AssistantMessage = ({ content, isStreaming }: { content: string, isStreaming?: boolean }) => {
  return (
    <div className="flex flex-col items-start w-full pr-12">
      <div className="text-xs font-semibold uppercase tracking-wider text-sahistra-text/40 mb-1 ml-4">Sahistra</div>
      <div className={`prose prose-sm md:prose-base prose-p:leading-relaxed prose-headings:font-serif prose-a:text-sahistra-accent px-4 py-1 text-sahistra-text ${isStreaming ? 'opacity-80' : ''}`}>
        <ReactMarkdown>{content}</ReactMarkdown>
      </div>
    </div>
  );
};
