package com.autoapply.agent.ui.screens

import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.test.StandardTestDispatcher
import kotlinx.coroutines.test.resetMain
import kotlinx.coroutines.test.runTest
import kotlinx.coroutines.test.setMain
import org.junit.After
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Before
import org.junit.Test
import org.mockito.kotlin.mock
import org.mockito.kotlin.whenever
import com.autoapply.agent.data.local.JobEntity
import com.autoapply.agent.data.remote.ScrapeRunResponse
import com.autoapply.agent.data.repository.JobRepository

@OptIn(ExperimentalCoroutinesApi::class)
class ScraperViewModelTest {

    private val testDispatcher = StandardTestDispatcher()
    private lateinit var repository: JobRepository
    private lateinit var viewModel: ScraperViewModel

    @Before
    fun setup() {
        Dispatchers.setMain(testDispatcher)
        repository = mock()
        viewModel = ScraperViewModel(repository)
    }

    @After
    fun tearDown() {
        Dispatchers.resetMain()
    }

    @Test
    fun `test_submitUrl_invalid shows error`() {
        viewModel.onUrlChanged("not-a-url")
        val isValid = viewModel.isValidUrl()

        assertEquals(false, isValid)
        assertNotNull(viewModel.uiState.value.urlError)
    }

    @Test
    fun `test_submitUrl_empty shows error`() {
        viewModel.onUrlChanged("")
        val isValid = viewModel.isValidUrl()

        assertEquals(false, isValid)
        assertEquals("URL cannot be empty", viewModel.uiState.value.urlError)
    }

    @Test
    fun `test_onUrlChanged clears previous error`() {
        viewModel.onUrlChanged("bad")
        viewModel.isValidUrl()
        assertNotNull(viewModel.uiState.value.urlError)

        viewModel.onUrlChanged("https://example.com")
        assertNull(viewModel.uiState.value.urlError)
    }

    @Test
    fun `test_resetState clears everything`() {
        viewModel.onUrlChanged("https://example.com")
        viewModel.resetState()

        val state = viewModel.uiState.value
        assertEquals("", state.url)
        assertNull(state.urlError)
        assertNull(state.scrapeRun)
        assertNull(state.resultJobId)
        assertNull(state.errorMessage)
    }

    @Test
    fun `test_submitUrl triggers submitting state`() = runTest {
        whenever(repository.scrapeUrl("https://example.com/jobs/1", null)).thenReturn(
            ScrapeRunResponse(
                id = 1,
                companyId = 1,
                status = "pending",
                jobsFound = 0,
                createdAt = "2024-01-01T00:00:00Z",
            )
        )

        viewModel.onUrlChanged("https://example.com/jobs/1")
        viewModel.submitUrl()

        // After calling submitUrl, state should show submitting
        assertTrue(viewModel.uiState.value.isSubmitting || viewModel.uiState.value.scrapeRun != null)
    }
}
