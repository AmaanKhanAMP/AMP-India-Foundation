"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_LINKS];

export default function NewFooterLinkPage() {
  return (
    <ContentFormPage
      {...config}
      title="New useful link"
      description="Add a link to the Footer Useful Links column."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
      defaults={{ status: "published" }}
    />
  );
}
