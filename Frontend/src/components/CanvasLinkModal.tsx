export function CanvasLinkModal({
  course,
  onConfirm,
  onCancel,
}: {
  course: any;
  onConfirm: () => void;
  onCancel: () => void;
}) {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-md max-w-md w-full p-6">
        <h3 className="text-lg font-semibold mb-2">Confirm Link</h3>
        <p className="text-sm text-muted-foreground mb-4">
          Are you sure you want to link <strong>{course.name}</strong> to this
          Canvas course?
        </p>
        <div className="flex justify-end gap-2">
          <button className="px-4 py-2 rounded border" onClick={onCancel}>
            Go back
          </button>
          <button
            className="px-4 py-2 rounded bg-primary text-white"
            onClick={onConfirm}
          >
            Link Course to Canvas
          </button>
        </div>
      </div>
    </div>
  );
}
