"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_GALLERY];

export default function NewHomeGalleryPage() {
  return (
    <ContentFormPage
      {...config}
      title="New gallery image"
      description="Upload a photo for the homepage Photo Gallery."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
      defaults={{ status: "published" }}
    />
  );
}
