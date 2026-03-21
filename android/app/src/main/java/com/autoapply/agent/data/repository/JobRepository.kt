package com.autoapply.agent.data.repository

import com.autoapply.agent.data.local.JobDao
import com.autoapply.agent.data.local.JobEntity
import com.autoapply.agent.data.remote.ApiService
import com.autoapply.agent.data.remote.JobResponse
import com.autoapply.agent.data.remote.ScrapeRunResponse
import com.autoapply.agent.data.remote.ScrapeURLRequest
import kotlinx.coroutines.flow.Flow
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class JobRepository @Inject constructor(
    private val apiService: ApiService,
    private val jobDao: JobDao,
) {
    /** Reactive stream of locally cached jobs. */
    fun getCachedJobs(): Flow<List<JobEntity>> = jobDao.getAll()

    /** Get a single cached job by ID. */
    suspend fun getCachedJobById(id: Int): JobEntity? = jobDao.getById(id)

    /** Fetch jobs from API, cache them locally, and return the response. */
    suspend fun fetchAndCacheJobs(
        query: String? = null,
        cohort: String? = null,
        page: Int = 1,
    ): List<JobEntity> {
        val response = apiService.getJobs(query = query, cohort = cohort, page = page)
        val entities = response.items.map { it.toEntity() }
        jobDao.insertAll(entities)
        return entities
    }

    /** Fetch a single job from API. */
    suspend fun fetchJob(jobId: Int): JobResponse {
        return apiService.getJob(jobId)
    }

    /** Trigger a scrape for a single URL. */
    suspend fun scrapeUrl(url: String, companyId: Int? = null): ScrapeRunResponse {
        return apiService.scrapeUrl(ScrapeURLRequest(url = url, companyId = companyId))
    }

    /** Poll the status of a scrape run. */
    suspend fun getScrapeStatus(runId: Int): ScrapeRunResponse {
        return apiService.getScrapeRun(runId)
    }

    /** Clear local cache. */
    suspend fun clearCache() = jobDao.deleteAll()

    /** Delete a job permanently. */
    suspend fun deleteJob(jobId: Int) {
        apiService.deleteJob(jobId)
        jobDao.deleteById(jobId)
    }
}

// ── Mapping ──────────────────────────────────────────────────────────────────

fun JobResponse.toEntity() = JobEntity(
    id = id,
    title = title,
    companyId = companyId,
    companyName = companyName,
    location = location,
    descriptionRaw = descriptionRaw,
    descriptionSummary = descriptionSummary,
    requirementsMustHave = requirements?.mustHave?.joinToString(","),
    requirementsNiceToHave = requirements?.niceToHave?.joinToString(","),
    requirementsYearsExperience = requirements?.yearsExperience,
    cohort = cohort,
    seniorityLevel = seniorityLevel,
    salaryMin = salaryMin,
    salaryMax = salaryMax,
    url = url,
    isActive = isActive,
    scrapedAt = scrapedAt,
    createdAt = createdAt,
    updatedAt = updatedAt,
)
