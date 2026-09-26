"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HERO_BANNERS];

export default function NewHeroBannerPage() {
  return (
    <ContentFormPage
      {...config}
      title="New hero banner"
      description="Upload a large banner image and configure CTAs."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
