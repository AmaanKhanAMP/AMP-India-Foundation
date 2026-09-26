"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.PAST_EVENTS];

export default function EditPastEventPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      resource={config.resource}
      basePath={config.basePath}
      folder={config.folder}
      fields={config.fields}
      id={id}
      title="Edit past event"
      description="Update past event details. Past Event Description appears on the public Events page card."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
