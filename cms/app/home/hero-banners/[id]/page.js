"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HERO_BANNERS];

export default function EditHeroBannerPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit hero banner"
      description="Update banner content and publish status."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
