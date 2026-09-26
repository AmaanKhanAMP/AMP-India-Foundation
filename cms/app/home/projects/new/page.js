"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES, STATUS_OPTIONS } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_PROJECTS];

/** Explicit field list — matches homepage Projects.jsx (image + title only). */
const HOME_PROJECT_FIELDS = [
  {
    name: "image_url",
    label: "Project image",
    type: "image",
    required: true,
    full: true,
    aspect: "video",
  },
  { name: "title", label: "Project title", required: true, full: true },
  { name: "display_order", label: "Display order", type: "number" },
  { name: "status", label: "Status", type: "select", options: STATUS_OPTIONS },
];

export default function NewHomeProjectPage() {
  return (
    <ContentFormPage
      resource={RESOURCES.HOME_PROJECTS}
      basePath={config.basePath}
      folder={config.folder}
      fields={HOME_PROJECT_FIELDS}
      title="New project"
      description="Add a homepage Latest Projects card (image and title)."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
      defaults={{ status: "published" }}
    />
  );
}
