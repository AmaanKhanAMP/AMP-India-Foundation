"use client";

import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.TESTIMONIALS];

export default function NewTestimonialPage() {
  return (
    <ContentFormPage
      {...config}
      title="New testimonial"
      description="Add a quote from a supporter or partner."
      breadcrumbs={crumbsFor(config, [{ label: "New" }])}
    />
  );
}
