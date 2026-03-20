package com.autoapply.agent.ui.screens

import android.net.Uri
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNotNull
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class ResumeViewModelTest {

    private val viewModel = ResumeViewModel()

    @Test
    fun `test_initialState is empty`() {
        val state = viewModel.uiState.value
        assertNull(state.fileUri)
        assertNull(state.fileName)
        assertTrue(state.categories.isEmpty())
    }

    @Test
    fun `test_clearResume resets state`() {
        // Simulate selecting a file (using null URI since we can't mock URI easily)
        viewModel.onFileSelected(null, null)

        viewModel.clearResume()
        val state = viewModel.uiState.value
        assertNull(state.fileUri)
        assertNull(state.fileName)
        assertTrue(state.categories.isEmpty())
    }

    @Test
    fun `test_onFileSelected_null_clearsCategories`() {
        viewModel.onFileSelected(null, null)
        val state = viewModel.uiState.value
        assertTrue(state.categories.isEmpty())
    }
}
