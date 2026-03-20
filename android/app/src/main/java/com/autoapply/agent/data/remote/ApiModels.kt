package com.autoapply.agent.data.remote

import com.squareup.moshi.Json
import com.squareup.moshi.JsonClass

// ── Request Models ───────────────────────────────────────────────────────────

@JsonClass(generateAdapter = true)
data class ScrapeURLRequest(
    val url: String,
    @Json(name = "company_id") val companyId: Int? = null,
)

// ── Response Models ──────────────────────────────────────────────────────────

@JsonClass(generateAdapter = true)
data class ScrapeRunResponse(
    val id: Int,
    @Json(name = "company_id") val companyId: Int,
    val status: String,
    @Json(name = "jobs_found") val jobsFound: Int,
    @Json(name = "started_at") val startedAt: String? = null,
    @Json(name = "finished_at") val finishedAt: String? = null,
    @Json(name = "error_message") val errorMessage: String? = null,
    @Json(name = "created_at") val createdAt: String,
)

@JsonClass(generateAdapter = true)
data class JobResponse(
    val id: Int,
    val title: String,
    @Json(name = "company_id") val companyId: Int,
    @Json(name = "company_name") val companyName: String? = null,
    val location: String? = null,
    @Json(name = "description_raw") val descriptionRaw: String? = null,
    @Json(name = "description_summary") val descriptionSummary: String? = null,
    val requirements: Requirements? = null,
    val cohort: String,
    @Json(name = "seniority_level") val seniorityLevel: String? = null,
    @Json(name = "salary_min") val salaryMin: Double? = null,
    @Json(name = "salary_max") val salaryMax: Double? = null,
    val url: String? = null,
    @Json(name = "is_active") val isActive: Boolean,
    @Json(name = "scraped_at") val scrapedAt: String? = null,
    @Json(name = "created_at") val createdAt: String,
    @Json(name = "updated_at") val updatedAt: String,
)

@JsonClass(generateAdapter = true)
data class Requirements(
    @Json(name = "must_have") val mustHave: List<String>? = null,
    @Json(name = "nice_to_have") val niceToHave: List<String>? = null,
    @Json(name = "years_experience") val yearsExperience: String? = null,
)

@JsonClass(generateAdapter = true)
data class JobListResponse(
    val items: List<JobResponse>,
    val total: Int,
    val page: Int,
    @Json(name = "page_size") val pageSize: Int,
    val pages: Int,
)
