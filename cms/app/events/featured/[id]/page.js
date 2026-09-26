"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FEATURED_EVENTS];

export default function EditFeaturedEventPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit featured event"
      description="Update featured event details."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
