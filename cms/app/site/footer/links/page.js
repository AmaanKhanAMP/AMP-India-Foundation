"use client";

import ContentListPage from "@/components/content/ContentListPage";
import { crumbsFor, resourceConfigs } from "@/utils/resourceConfigs";
import { RESOURCES } from "@/utils/constants";

const config = resourceConfigs[RESOURCES.FOOTER_LINKS];

export default function FooterLinksPage() {
  return <ContentListPage {...config} breadcrumbs={crumbsFor(config)} />;
}
