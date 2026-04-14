"use client";

import { useState, useTransition } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { submitRetailReport, uploadSubmissionProof } from "@/lib/api";

type MessageState =
  | { tone: "success"; text: string }
  | { tone: "error"; text: string }
  | { tone: "info"; text: string }
  | null;

function normalizeSubmissionPayload(formData: FormData, uploadedAssetPath: string | null) {
  const payload: Record<string, string> = {
    item_name: String(formData.get("item_name") ?? "").trim(),
    price: String(formData.get("price") ?? "").trim(),
    currency: String(formData.get("currency") ?? "USD").trim() || "USD",
  };

  for (const field of ["store", "city", "country", "date_seen", "notes"] as const) {
    const value = String(formData.get(field) ?? "").trim();
    if (value) {
      payload[field] = value;
    }
  }

  const manualProofUrl = String(formData.get("receipt_asset_url") ?? "").trim();
  const proofPath = uploadedAssetPath ?? manualProofUrl;
  if (proofPath) {
    payload.receipt_asset_url = proofPath;
  }

  return payload;
}

export function SubmissionForm() {
  const [isPending, startTransition] = useTransition();
  const [state, setState] = useState<MessageState>(null);
  const [uploadedProofLabel, setUploadedProofLabel] = useState<string | null>(null);

  return (
    <form
      className="panel grid gap-4 p-6"
      onSubmit={(event) => {
        event.preventDefault();
        const form = event.currentTarget;
        const formData = new FormData(form);
        startTransition(async () => {
          try {
            const proofFile = formData.get("receipt_file");
            let uploadedAssetPath: string | null = null;
            if (proofFile instanceof File && proofFile.size > 0) {
              setState({ tone: "info", text: "Uploading receipt proof..." });
              const uploaded = await uploadSubmissionProof(proofFile);
              uploadedAssetPath = uploaded.asset_path;
              setUploadedProofLabel(`${uploaded.file_name} uploaded`);
            }

            const payload = normalizeSubmissionPayload(formData, uploadedAssetPath);
            await submitRetailReport(payload);
            setState({ tone: "success", text: "Submission received and queued for moderation." });
            setUploadedProofLabel(null);
            form.reset();
          } catch (error) {
            setState({
              tone: "error",
              text: error instanceof Error ? error.message : "Submission failed. Please try again.",
            });
          }
        });
      }}
    >
      <div className="grid gap-4 md:grid-cols-2">
        <Input name="item_name" placeholder="Item name" required />
        <Input name="price" placeholder="Price" required />
        <Input defaultValue="USD" name="currency" placeholder="Currency" />
        <Input name="store" placeholder="Store" />
        <Input name="city" placeholder="City" />
        <Input name="country" placeholder="Country" />
        <Input name="date_seen" placeholder="YYYY-MM-DD" />
      </div>
      <div className="grid gap-3 md:grid-cols-2">
        <label className="grid gap-2 text-sm text-parchment/75">
          <span>Upload receipt image or PDF</span>
          <input
            accept="image/jpeg,image/png,image/webp,application/pdf"
            className="rounded-2xl border border-white/10 bg-white/5 px-4 py-3 text-sm text-parchment file:mr-3 file:rounded-full file:border-0 file:bg-bronze file:px-3 file:py-2 file:text-xs file:uppercase file:tracking-[0.2em] file:text-black"
            name="receipt_file"
            type="file"
          />
        </label>
        <Input name="receipt_asset_url" placeholder="External proof URL (optional fallback)" />
      </div>
      <Input name="notes" placeholder="Notes" />
      <div className="flex items-center justify-between gap-3">
        <div className="text-sm text-parchment/60">
          <p>Receipt-backed reports will be scored more confidently after moderation.</p>
          <p className="mt-1 text-xs text-parchment/45">Accepted uploads: JPG, PNG, WEBP, PDF up to 8 MB.</p>
          {uploadedProofLabel ? <p className="mt-1 text-xs text-bronze">{uploadedProofLabel}</p> : null}
        </div>
        <Button disabled={isPending} type="submit">
          {isPending ? "Submitting..." : "Submit report"}
        </Button>
      </div>
      {state ? (
        <p className={`text-sm ${state.tone === "error" ? "text-red-300" : state.tone === "success" ? "text-moss" : "text-bronze"}`}>
          {state.text}
        </p>
      ) : null}
    </form>
  );
}
