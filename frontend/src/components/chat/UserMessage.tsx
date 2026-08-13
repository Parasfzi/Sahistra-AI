export const UserMessage = ({ content }: { content: string }) => {
  return (
    <div className="flex flex-col items-end w-full pl-12">
      <div className="bg-sahistra-card px-5 py-3 rounded-2xl rounded-tr-sm shadow-sm border border-sahistra-text/5 max-w-[85%]">
        <p className="text-sahistra-text whitespace-pre-wrap leading-relaxed">{content}</p>
      </div>
    </div>
  );
};
