package com.autoapply.agent.data.repository

import com.autoapply.agent.data.local.JobDao
import com.autoapply.agent.data.local.JobEntity
import com.autoapply.agent.data.remote.ApiService
import com.autoapply.agent.data.remote.JobListResponse
import com.autoapply.agent.data.remote.JobResponse
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.flowOf
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.any
import org.mockito.kotlin.mock
import org.mockito.kotlin.verify
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class JobRepositoryTest {

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var apiService: ApiService
    private lateinit var jobDao: JobDao
    private lateinit var repository: JobRepository

    private val sampleApiJob = JobResponse(
        id = 1, title = "Engineer", companyId = 1,
        companyName = "Acme", cohort = "Backend", isActive = true,
        createdAt = "2024-01-01", updatedAt = "2024-01-01",
    )

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        apiService = mock()
        jobDao = mock()
        repository = JobRepository(apiService, jobDao)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `test_fetchJobs_cachesInRoom`() = runTest {
        whenever(apiService.getJobs(null, null, null, null, null, true, null, 1, 20))
            .thenReturn(
                JobListResponse(
                    items = listOf(sampleApiJob),
                    total = 1, page = 1, pageSize = 20, pages = 1,
                )
            )

        val result = repository.fetchAndCacheJobs()

        assertEquals(1, result.size)
        assertEquals("Engineer", result[0].title)
        verify(jobDao).insertAll(any())
    }

    @Test
    fun `test_getJobs_offlineMode returns cached`() = runTest {
        val cached = listOf(
            JobEntity(
                id = 1, title = "Cached Job", companyId = 1,
                cohort = "Backend", isActive = true,
                createdAt = "2024-01-01", updatedAt = "2024-01-01",
            )
        )
        whenever(jobDao.getAll()).thenReturn(flowOf(cached))

        repository.getCachedJobs().collect { jobs ->
            assertEquals(1, jobs.size)
            assertEquals("Cached Job", jobs[0].title)
        }
    }

    @Test
    fun `test_fetchJobs_networkError throws`() = runTest {
        whenever(apiService.getJobs(null, null, null, null, null, true, null, 1, 20))
            .thenThrow(RuntimeException("Network unavailable"))

        var errorCaught = false
        try {
            repository.fetchAndCacheJobs()
        } catch (e: Exception) {
            errorCaught = true
            assertEquals("Network unavailable", e.message)
        }
        assertTrue(errorCaught)
    }
}
