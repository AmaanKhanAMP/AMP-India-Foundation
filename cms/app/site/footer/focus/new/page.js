"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_FOCUS];

export default function NewFooterFocusPage() {
  return (
    <ContentFormPage
      {...config}
      title="New recent focus item"
      description="Add an item to the Footer Recent Focus column."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
      defaults={{ status: "published" }}
    />
  );
}
