package com.autoapply.agent.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.Cancel
import androidx.compose.material.icons.filled.Download
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Work
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.autoapply.agent.data.local.JobEntity

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun JobDetailScreen(
    jobId: Int,
    onNavigateBack: () -> Unit,
    viewModel: JobsViewModel = hiltViewModel(),
) {
    val jobs by viewModel.jobs.collectAsState()
    val uiState by viewModel.uiState.collectAsState()
    var showModifyResume by remember { mutableStateOf(false) }

    val job = jobs.find { it.id == jobId }
    val isLoading = uiState.isLoading

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text(job?.title ?: "Job Details") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(
                            Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "Back",
                        )
                    }
                },
            )
        },
    ) { padding ->
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                CircularProgressIndicator()
            }
        } else if (job == null) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding),
                contentAlignment = Alignment.Center,
            ) {
                Text("Job not found")
            }
        } else {
            val j = job!!
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
                    .padding(16.dp)
                    .verticalScroll(rememberScrollState()),
            ) {
                // Title
                Text(
                    text = j.title,
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold,
                )

                Spacer(modifier = Modifier.height(8.dp))

                // Company and Location
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(16.dp),
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            Icons.Default.Work,
                            contentDescription = null,
                            tint = MaterialTheme.colorScheme.primary,
                        )
                        Text(
                            text = j.companyName ?: "Unknown",
                            modifier = Modifier.padding(start = 4.dp),
                        )
                    }
                    if (j.location != null) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                Icons.Default.LocationOn,
                                contentDescription = null,
                                tint = MaterialTheme.colorScheme.primary,
                            )
                            Text(text = j.location, modifier = Modifier.padding(start = 4.dp))
                        }
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                // Chips: Cohort, Seniority
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    AssistChip(onClick = {}, label = { Text(j.cohort) })
                    j.seniorityLevel?.let {
                        AssistChip(onClick = {}, label = { Text(it) })
                    }
                }

                // Salary
                if (j.salaryMin != null || j.salaryMax != null) {
                    Spacer(modifier = Modifier.height(8.dp))
                    val salary = buildString {
                        append("💰 ")
                        j.salaryMin?.let { append("$${it.toInt()}") }
                        if (j.salaryMin != null && j.salaryMax != null) append(" – ")
                        j.salaryMax?.let { append("$${it.toInt()}") }
                    }
                    Text(
                        text = salary,
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.primary,
                    )
                }

                Spacer(modifier = Modifier.height(16.dp))

                // Summary
                if (j.descriptionSummary != null) {
                    SectionCard("Summary") {
                        Text(j.descriptionSummary)
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }

                // Requirements
                val mustHave = j.requirementsMustHave
                    ?.split(",")
                    ?.filter { it.isNotBlank() }
                    ?: emptyList()
                val niceToHave = j.requirementsNiceToHave
                    ?.split(",")
                    ?.filter { it.isNotBlank() }
                    ?: emptyList()

                if (mustHave.isNotEmpty()) {
                    SectionCard("Must Have") {
                        mustHave.forEach { Text("• $it") }
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }

                if (niceToHave.isNotEmpty()) {
                    SectionCard("Nice to Have") {
                        niceToHave.forEach { Text("• $it") }
                    }
                    Spacer(modifier = Modifier.height(12.dp))
                }

                j.requirementsYearsExperience?.let {
                    Text(
                        text = "Experience: $it",
                        style = MaterialTheme.typography.bodyLarge,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Spacer(modifier = Modifier.height(16.dp))
                }

                // Modify Resume Button
                if (!showModifyResume) {
                    Button(
                        onClick = { showModifyResume = true },
                        modifier = Modifier.fillMaxWidth(),
                    ) {
                        Icon(Icons.Default.Edit, contentDescription = null)
                        Text("  Modify Resume for This Job")
                    }
                } else {
                    Card(
                        modifier = Modifier.fillMaxWidth(),
                        colors = CardDefaults.cardColors(
                            containerColor = MaterialTheme.colorScheme.secondaryContainer,
                        ),
                    ) {
                        Column(modifier = Modifier.padding(16.dp)) {
                            Text(
                                text = "Resume Modification",
                                style = MaterialTheme.typography.titleMedium,
                            )
                            Text(
                                text = "Backend not yet implemented. "
                                    + "This will tailor your resume to match this job.",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.onSurfaceVariant,
                                modifier = Modifier.padding(vertical = 8.dp),
                            )
                            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Button(onClick = { /* TODO: Download */ }) {
                                    Icon(Icons.Default.Download, contentDescription = null)
                                    Text("  Download")
                                }
                                OutlinedButton(onClick = { showModifyResume = false }) {
                                    Icon(Icons.Default.Cancel, contentDescription = null)
                                    Text("  Cancel")
                                }
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun SectionCard(
    title: String,
    content: @Composable () -> Unit,
) {
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant,
        ),
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.primary,
                fontWeight = FontWeight.SemiBold,
            )
            Spacer(modifier = Modifier.height(8.dp))
            content()
        }
    }
}
