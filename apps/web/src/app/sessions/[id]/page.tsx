import { Workbench } from "@/features/replay/workbench";
export default async function SessionPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>;
  searchParams: Promise<{ tab?: string }>;
}) {
  const { id } = await params;
  const { tab } = await searchParams;
  return (
    <Workbench
      key={id}
      id={id}
      initialTab={tab === "data" || tab === "research" ? tab : "replay"}
    />
  );
}
