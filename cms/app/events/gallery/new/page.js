"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.PAST_EVENTS];

export default function NewPastEventPage() {
  return (
    <ContentFormPage
      resource={config.resource}
      basePath={config.basePath}
      folder={config.folder}
      fields={config.fields}
      title="New past event"
      description="Add a past event to the Events page grid. Include a Past Event Description for the card body."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
