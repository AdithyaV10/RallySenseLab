import { PrintReport } from "@/features/research/print-report";
export default async function ReportPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <PrintReport id={id} />;
}
