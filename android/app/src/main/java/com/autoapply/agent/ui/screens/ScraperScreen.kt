package com.autoapply.agent.ui.screens

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Link
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun ScraperScreen(
    onNavigateToJobDetail: (Int) -> Unit,
    viewModel: ScraperViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Text(
            text = "Job Scraper",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary,
        )

        Spacer(modifier = Modifier.height(8.dp))

        Text(
            text = "Enter a job posting URL to scrape and parse",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(modifier = Modifier.height(24.dp))

        // URL Input
        OutlinedTextField(
            value = state.url,
            onValueChange = viewModel::onUrlChanged,
            label = { Text("Job URL") },
            placeholder = { Text("https://company.com/careers/job-123") },
            leadingIcon = { Icon(Icons.Default.Link, contentDescription = null) },
            isError = state.urlError != null,
            supportingText = state.urlError?.let { { Text(it) } },
            singleLine = true,
            modifier = Modifier.fillMaxWidth(),
            enabled = !state.isSubmitting,
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Submit Button
        Button(
            onClick = viewModel::submitUrl,
            enabled = !state.isSubmitting && state.url.isNotBlank(),
            modifier = Modifier.fillMaxWidth(),
        ) {
            if (state.isSubmitting) {
                CircularProgressIndicator(
                    modifier = Modifier.size(20.dp),
                    strokeWidth = 2.dp,
                    color = MaterialTheme.colorScheme.onPrimary,
                )
                Text("  Scraping...", modifier = Modifier.padding(start = 8.dp))
            } else {
                Text("Submit")
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Status Card
        AnimatedVisibility(visible = state.scrapeRun != null || state.errorMessage != null) {
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = when {
                        state.errorMessage != null -> MaterialTheme.colorScheme.errorContainer
                        state.scrapeRun?.status == "completed" ->
                            MaterialTheme.colorScheme.primaryContainer
                        else -> MaterialTheme.colorScheme.surfaceVariant
                    },
                ),
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    if (state.errorMessage != null) {
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            Icon(
                                Icons.Default.Error,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.error,
                            )
                            Text(
                                text = state.errorMessage!!,
                                color = MaterialTheme.colorScheme.onErrorContainer,
                            )
                        }
                    } else {
                        val run = state.scrapeRun!!
                        Row(
                            verticalAlignment = Alignment.CenterVertically,
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                        ) {
                            if (run.status == "completed") {
                                Icon(
                                    Icons.Default.CheckCircle,
                                    contentDescription = null,
                                    tint = MaterialTheme.colorScheme.primary,
                                )
                            } else {
                                CircularProgressIndicator(modifier = Modifier.size(20.dp))
                            }
                            Text(
                                text = "Status: ${run.status.uppercase()}",
                                style = MaterialTheme.typography.titleSmall,
                            )
                        }
                        if (run.jobsFound > 0) {
                            Text(
                                text = "Jobs found: ${run.jobsFound}",
                                style = MaterialTheme.typography.bodyMedium,
                                modifier = Modifier.padding(top = 4.dp),
                            )
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Check Button — appears after successful scrape
        AnimatedVisibility(visible = state.resultJobId != null) {
            OutlinedButton(
                onClick = { state.resultJobId?.let(onNavigateToJobDetail) },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Text("Check Job Details")
            }
        }
    }
}
