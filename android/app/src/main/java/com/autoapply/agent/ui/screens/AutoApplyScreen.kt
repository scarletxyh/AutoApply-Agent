package com.autoapply.agent.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Pause
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel

@Composable
fun AutoApplyScreen(
    onNavigateToProfile: () -> Unit,
    viewModel: AutoApplyViewModel = hiltViewModel(),
) {
    val state by viewModel.uiState.collectAsState()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Text(
            text = "Auto-Apply Agent",
            style = MaterialTheme.typography.headlineMedium,
            color = MaterialTheme.colorScheme.primary,
        )

        Spacer(modifier = Modifier.height(4.dp))

        Text(
            text = "Automate your job applications",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Profile Setup
        OutlinedButton(
            onClick = onNavigateToProfile,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Icon(Icons.Default.Person, contentDescription = null)
            Text("  Edit Profile", modifier = Modifier.padding(start = 4.dp))
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Mode Toggle
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = MaterialTheme.colorScheme.surfaceVariant,
            ),
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Column {
                    Text(
                        text = if (state.isAutoSubmit) "Auto-Submit" else "Manual Review",
                        style = MaterialTheme.typography.titleMedium,
                        fontWeight = FontWeight.SemiBold,
                    )
                    Text(
                        text = if (state.isAutoSubmit) {
                            "Agent will submit automatically"
                        } else {
                            "Agent will pause for your review"
                        },
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                    )
                }
                Switch(
                    checked = state.isAutoSubmit,
                    onCheckedChange = viewModel::toggleAutoSubmit,
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Agent Status
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(
                containerColor = when (state.agentState) {
                    AgentState.RUNNING -> MaterialTheme.colorScheme.primaryContainer
                    AgentState.PAUSED -> MaterialTheme.colorScheme.tertiaryContainer
                    AgentState.NEEDS_INPUT -> MaterialTheme.colorScheme.errorContainer
                    AgentState.IDLE -> MaterialTheme.colorScheme.surfaceVariant
                },
            ),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "Agent Status",
                    style = MaterialTheme.typography.titleMedium,
                )
                Spacer(modifier = Modifier.height(4.dp))
                Text(
                    text = when (state.agentState) {
                        AgentState.IDLE -> "⚪ Idle — Ready to start"
                        AgentState.RUNNING -> "🟢 Running — Processing applications..."
                        AgentState.PAUSED -> "🟡 Paused"
                        AgentState.NEEDS_INPUT -> "🔴 Needs Input — Waiting for your help"
                    },
                    style = MaterialTheme.typography.bodyLarge,
                )
                Text(
                    text = "Processed: ${state.processedCount} applications",
                    style = MaterialTheme.typography.bodyMedium,
                    modifier = Modifier.padding(top = 4.dp),
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Controls
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            when (state.agentState) {
                AgentState.IDLE -> {
                    Button(
                        onClick = viewModel::startAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Text("  Start")
                    }
                }
                AgentState.RUNNING -> {
                    OutlinedButton(
                        onClick = viewModel::pauseAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.Pause, contentDescription = null)
                        Text("  Pause")
                    }
                    Button(
                        onClick = viewModel::stopAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = null)
                        Text("  Stop")
                    }
                }
                AgentState.PAUSED -> {
                    Button(
                        onClick = viewModel::startAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.PlayArrow, contentDescription = null)
                        Text("  Resume")
                    }
                    OutlinedButton(
                        onClick = viewModel::stopAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = null)
                        Text("  Stop")
                    }
                }
                AgentState.NEEDS_INPUT -> {
                    Button(
                        onClick = viewModel::stopAgent,
                        modifier = Modifier.weight(1f),
                    ) {
                        Icon(Icons.Default.Stop, contentDescription = null)
                        Text("  Stop")
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Simulate uncertain field (for demo)
        if (state.agentState == AgentState.RUNNING) {
            OutlinedButton(
                onClick = { viewModel.simulateUncertainField("Years of Experience") },
                modifier = Modifier.fillMaxWidth(),
            ) {
                Icon(Icons.Default.Error, contentDescription = null)
                Text("  Simulate Uncertain Field")
            }
        }

        // Alert Dialog for uncertain fields
        if (state.agentState == AgentState.NEEDS_INPUT && state.uncertainField != null) {
            AlertDialog(
                onDismissRequest = {},
                title = { Text("Manual Input Required") },
                text = {
                    Text(
                        "The agent is uncertain about the field: "
                            + "\"${state.uncertainField}\". "
                            + "Please review before continuing."
                    )
                },
                confirmButton = {
                    TextButton(onClick = viewModel::resolveUncertainField) {
                        Text("Continue")
                    }
                },
                dismissButton = {
                    TextButton(onClick = viewModel::stopAgent) {
                        Text("Stop Agent")
                    }
                },
            )
        }
    }
}
