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
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm">
      <div className="max-w-md w-full p-6 rounded-md bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100 ring-1 ring-slate-200 dark:ring-slate-700">
        <h3 className="text-lg font-semibold mb-2">Confirm Link</h3>
        <p className="text-sm text-slate-700 dark:text-slate-300 mb-4">
          Are you sure you want to link <strong>{course.name}</strong> to this
          Canvas course?
        </p>

        <div className="flex justify-end gap-2">
          <button
            onClick={onCancel}
            className="px-4 py-2 rounded border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 bg-white dark:bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/30"
          >
            Go back
          </button>
          <button
            onClick={onConfirm}
            className="px-4 py-2 rounded border border-slate-300 dark:border-slate-700 text-slate-700 dark:text-slate-200 bg-white dark:bg-transparent hover:bg-slate-50 dark:hover:bg-slate-800 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/30"
          >
            Link Course to Canvas
          </button>
        </div>
      </div>
    </div>
  );
}
