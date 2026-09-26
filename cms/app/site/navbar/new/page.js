"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.NAVBAR_ITEMS];

export default function NewNavbarItemPage() {
  return (
    <ContentFormPage
      {...config}
      title="New navbar item"
      description="Add a top-level link or a Projects dropdown child."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
      defaults={{ item_type: "link", status: "published" }}
    />
  );
}
