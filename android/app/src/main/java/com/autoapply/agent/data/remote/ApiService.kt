package com.autoapply.agent.data.remote

import okhttp3.MultipartBody
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface ApiService {

    @POST("api/v1/scrape/url")
    suspend fun scrapeUrl(@Body request: ScrapeURLRequest): ScrapeRunResponse

    @GET("api/v1/scrape/{runId}")
    suspend fun getScrapeRun(@Path("runId") runId: Int): ScrapeRunResponse

    @GET("api/v1/jobs")
    suspend fun getJobs(
        @Query("query") query: String? = null,
        @Query("cohort") cohort: String? = null,
        @Query("location") location: String? = null,
        @Query("seniority_level") seniorityLevel: String? = null,
        @Query("company_id") companyId: Int? = null,
        @Query("is_active") isActive: Boolean? = true,
        @Query("min_salary") minSalary: Double? = null,
        @Query("page") page: Int = 1,
        @Query("page_size") pageSize: Int = 20,
    ): JobListResponse

    @GET("api/v1/jobs/{jobId}")
    suspend fun getJob(@Path("jobId") jobId: Int): JobResponse

    @retrofit2.http.DELETE("api/v1/jobs/{jobId}")
    suspend fun deleteJob(@Path("jobId") jobId: Int)

    // ── Resumes ────────────────────────────────────────────────────────────────
    
    @retrofit2.http.POST("api/v1/resumes/upload")
    @retrofit2.http.Multipart
    suspend fun uploadResume(@retrofit2.http.Part file: MultipartBody.Part): ResumeResponse

    @GET("api/v1/resumes/")
    suspend fun getResumes(): List<ResumeResponse>

    @retrofit2.http.DELETE("api/v1/resumes/{resumeId}")
    suspend fun deleteResume(@Path("resumeId") resumeId: Int)
}
