package com.autoapply.agent.ui.screens

import androidx.compose.foundation.layout.Arrangement
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
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Save
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.InputChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun ProfileScreen(
    onNavigateBack: () -> Unit,
    viewModel: ProfileViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()
    val snackbarHostState = remember { SnackbarHostState() }

    LaunchedEffect(state.isSaved) {
        if (state.isSaved) {
            snackbarHostState.showSnackbar("Profile saved!")
        }
    }

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile Configuration") },
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
        snackbarHost = { SnackbarHost(snackbarHostState) },
    ) { padding ->
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            // ── Personal Information ─────────────────────────────────────────
            Text(
                text = "Personal Information",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary,
            )

            OutlinedTextField(
                value = state.fullName,
                onValueChange = { viewModel.onFieldChanged("fullName", it) },
                label = { Text("Full Name") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.email,
                onValueChange = { viewModel.onFieldChanged("email", it) },
                label = { Text("Email") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.phone,
                onValueChange = { viewModel.onFieldChanged("phone", it) },
                label = { Text("Phone") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.linkedin,
                onValueChange = { viewModel.onFieldChanged("linkedin", it) },
                label = { Text("LinkedIn URL") },
                modifier = Modifier.fillMaxWidth(),
            )
            OutlinedTextField(
                value = state.github,
                onValueChange = { viewModel.onFieldChanged("github", it) },
                label = { Text("GitHub URL") },
                modifier = Modifier.fillMaxWidth(),
            )

            Spacer(modifier = Modifier.height(8.dp))

            // ── Technical Skills ─────────────────────────────────────────────
            Text(
                text = "Technical Skills",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary,
            )

            Row(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                modifier = Modifier.fillMaxWidth(),
            ) {
                OutlinedTextField(
                    value = state.newSkill,
                    onValueChange = { viewModel.onFieldChanged("newSkill", it) },
                    label = { Text("Add skill") },
                    singleLine = true,
                    modifier = Modifier.weight(1f),
                )
                IconButton(onClick = viewModel::addSkill) {
                    Icon(Icons.Default.Add, contentDescription = "Add")
                }
            }

            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                state.skills.forEach { skill ->
                    InputChip(
                        selected = false,
                        onClick = { viewModel.removeSkill(skill) },
                        label = { Text(skill) },
                        trailingIcon = {
                            Icon(
                                Icons.Default.Close,
                                contentDescription = "Remove",
                            )
                        },
                    )
                }
            }

            Spacer(modifier = Modifier.height(8.dp))

            // ── Work Experience ──────────────────────────────────────────────
            Text(
                text = "Work Experience",
                style = MaterialTheme.typography.titleLarge,
                color = MaterialTheme.colorScheme.primary,
            )

            state.experiences.forEachIndexed { index, exp ->
                Card(
                    modifier = Modifier.fillMaxWidth(),
                    colors = CardDefaults.cardColors(
                        containerColor = MaterialTheme.colorScheme.surfaceVariant,
                    ),
                ) {
                    Column(modifier = Modifier.padding(12.dp)) {
                        Row(
                            modifier = Modifier.fillMaxWidth(),
                            horizontalArrangement = Arrangement.SpaceBetween,
                        ) {
                            Text(
                                text = "Experience #${index + 1}",
                                style = MaterialTheme.typography.labelLarge,
                            )
                            if (state.experiences.size > 1) {
                                IconButton(
                                    onClick = { viewModel.removeExperience(index) },
                                ) {
                                    Icon(Icons.Default.Delete, contentDescription = "Remove")
                                }
                            }
                        }
                        OutlinedTextField(
                            value = exp.company,
                            onValueChange = {
                                viewModel.updateExperience(index, exp.copy(company = it))
                            },
                            label = { Text("Company") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        OutlinedTextField(
                            value = exp.title,
                            onValueChange = {
                                viewModel.updateExperience(index, exp.copy(title = it))
                            },
                            label = { Text("Title") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        OutlinedTextField(
                            value = exp.duration,
                            onValueChange = {
                                viewModel.updateExperience(index, exp.copy(duration = it))
                            },
                            label = { Text("Duration (e.g. Jun 2024 – Sep 2024)") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                        OutlinedTextField(
                            value = exp.description,
                            onValueChange = {
                                viewModel.updateExperience(index, exp.copy(description = it))
                            },
                            label = { Text("Description") },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 3,
                        )
                    }
                }
            }

            OutlinedButton(
                onClick = viewModel::addExperience,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Default.Add, contentDescription = null)
                Text("  Add Experience")
            }

            Spacer(modifier = Modifier.height(16.dp))

            // ── Save ─────────────────────────────────────────────────────────
            Button(
                onClick = viewModel::saveProfile,
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Default.Save, contentDescription = null)
                Text("  Save Profile")
            }

            Spacer(modifier = Modifier.height(32.dp))
        }
    }
}
