"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FEATURED_EVENTS];

export default function NewFeaturedEventPage() {
  return (
    <ContentFormPage
      {...config}
      title="New featured event"
      description="Highlight a key event on the Events page."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
