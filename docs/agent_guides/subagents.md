# Subagents Guide

Use this guide only when a task may benefit from bounded parallel work.

## Default

Default to a single agent.

Subagents are optional, not automatic.

## Good use cases

Use subagents for:
- repository exploration;
- independent test runs;
- log analysis;
- summarizing separate modules;
- comparing approaches;
- finding duplicated patterns.

## Bad use cases

Avoid subagents for:
- small fixes;
- edits touching the same files;
- shared architecture decisions;
- refactors across common modules;
- tasks where one consistent mental model is required.

## Limits

No more than 2 subagents at a time unless the user explicitly asks otherwise.

Each subagent must have:
- a narrow task;
- clear boundaries;
- no overlapping file edits;
- concise output.

## Required subagent output

Subagents should return:
- what they inspected;
- key findings;
- suggested action;
- risks;
- relevant files.

They should not return:
- raw logs;
- huge file dumps;
- unrelated advice;
- final architectural decisions.

The main agent remains responsible for:
- final decision;
- consistency;
- implementation;
- diff quality;
- final user report.
