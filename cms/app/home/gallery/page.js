"use client";

import ContentListPage from "@/components/content/ContentListPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.HOME_GALLERY];

export default function HomeGalleryPage() {
  return <ContentListPage {...config} breadcrumbs={crumbsFor(config)} />;
}
