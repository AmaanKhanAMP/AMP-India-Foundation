"use client";

import { use } from "react";
import ContentFormPage from "@/components/content/ContentFormPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.TESTIMONIALS];

export default function EditTestimonialPage({ params }) {
  const { id } = use(params);
  return (
    <ContentFormPage
      {...config}
      id={id}
      title="Edit testimonial"
      description="Update testimonial details."
      breadcrumbs={crumbsFor(config, [{ label: "Edit" }])}
    />
  );
}
