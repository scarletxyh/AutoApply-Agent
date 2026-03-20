package com.autoapply.agent.ui.screens

import app.cash.turbine.test
import com.autoapply.agent.data.local.JobEntity
import com.autoapply.agent.data.repository.JobRepository
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
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever

@OptIn(ExperimentalCoroutinesApi::class)
class JobsViewModelTest {

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var repository: JobRepository
    private lateinit var viewModel: JobsViewModel

    private val sampleJobs = listOf(
        JobEntity(
            id = 1, title = "Backend Engineer", companyId = 1,
            companyName = "Acme", cohort = "Backend", isActive = true,
            createdAt = "2024-01-01", updatedAt = "2024-01-01",
        ),
        JobEntity(
            id = 2, title = "Frontend Developer", companyId = 1,
            companyName = "Acme", cohort = "Frontend", isActive = true,
            createdAt = "2024-01-02", updatedAt = "2024-01-02",
        ),
    )

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        repository = mock()
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `test_loadJobs_emitsFromRepository`() = runTest {
        whenever(repository.getCachedJobs()).thenReturn(flowOf(sampleJobs))
        whenever(repository.fetchAndCacheJobs(null, null, 1)).thenReturn(sampleJobs)

        viewModel = JobsViewModel(repository)

        viewModel.jobs.test {
            val initial = awaitItem()
            // First emission may be empty or the sample jobs
            if (initial.isEmpty()) {
                val populated = awaitItem()
                assertEquals(2, populated.size)
            } else {
                assertEquals(2, initial.size)
            }
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun `test_emptyState returns empty list`() = runTest {
        whenever(repository.getCachedJobs()).thenReturn(flowOf(emptyList()))
        whenever(repository.fetchAndCacheJobs(null, null, 1)).thenReturn(emptyList())

        viewModel = JobsViewModel(repository)

        viewModel.jobs.test {
            val jobs = awaitItem()
            assertTrue(jobs.isEmpty())
            cancelAndConsumeRemainingEvents()
        }
    }

    @Test
    fun `test_loadJobs_networkError shows fallback message`() = runTest {
        whenever(repository.getCachedJobs()).thenReturn(flowOf(sampleJobs))
        whenever(repository.fetchAndCacheJobs(null, null, 1))
            .thenThrow(RuntimeException("Network error"))

        viewModel = JobsViewModel(repository)
        testDispatcher.scheduler.advanceUntilIdle()

        assertEquals(
            "Failed to load jobs. Showing cached data.",
            viewModel.uiState.value.errorMessage,
        )
    }
}
