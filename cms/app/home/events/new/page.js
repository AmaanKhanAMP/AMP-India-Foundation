"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_EVENTS];

export default function NewHomeEventPage() {
  return (
    <ContentFormPage
      {...config}
      title="New home event"
      description="Add an upcoming event teaser for the homepage."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
