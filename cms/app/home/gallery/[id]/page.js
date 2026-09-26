"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_GALLERY];

export default function EditHomeGalleryPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit gallery image"
      description="Update the homepage Photo Gallery image or alt text."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
