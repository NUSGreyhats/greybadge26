#pragma once
#include <stdio.h>

/* ── MCQ quiz (CH1) ─────────────────────────────────────────── */
/* Questions, options and per-question replies live in quiz_data.h — edit that
 * file to customise the quiz. This code just drives it. */
#include "quiz_data.h"

static int  ch1_q       = 0;
static bool ch1_done    = false;
static bool ch1_waiting = false; /* waiting for answer input */

/* Print one question with auto-generated a/b/c/d option labels. */
static void ch1_print_question(int idx)
{
    printf("\n%s\n", quiz[idx].question);
    for (int i = 0; i < 4; i++)
        printf("  %c) %s\n", 'a' + i, quiz[idx].options[i]);
    printf("Your answer (a/b/c/d): ");
    fflush(stdout);
}

void setupCH1(void)
{
    ch1_q       = 0;
    ch1_done    = false;
    ch1_waiting = true;
    printf("\n==========================\n");
    printf("  CHALLENGE 1\n");
    printf("  Welcome to GreyFlag!\n");
    printf("==========================\n");
    printf("Answer all %d questions correctly to get your flag.\n", (int)QUIZ_LEN);
    ch1_print_question(0);
}

/* returns true when challenge is complete (back to menu) */
bool runCH1(char c)
{
    if (ch1_done || !ch1_waiting) return false;
    if (c == '\n' || c == '\r') return false;

    char ans = (char)(c | 0x20); /* lowercase */
    if (ans < 'a' || ans > 'd') {
        printf("\nInvalid. Enter a, b, c, or d: ");
        fflush(stdout);
        return false;
    }

    printf("%c\n", ans);

    if (ans != quiz[ch1_q].answer) {
        const char *rw = quiz[ch1_q].reply_wrong;
        printf("%s\n", (rw && rw[0]) ? rw : "Not quite - try again.");
        ch1_print_question(ch1_q);   /* re-ask the same question, keep progress */
        return false;
    }

    const char *rc = quiz[ch1_q].reply_correct;
    printf("%s\n", (rc && rc[0]) ? rc : "Correct!");
    ch1_q++;

    if (ch1_q >= (int)QUIZ_LEN) {
        printf("\n*** FLAG: %s ***\n", QUIZ_FLAG); // level 0 flag for dumping the firmware
        printf("\nAmong other things, you can press [0] at ANY time to return to menu. \nHolding the boot button (U7, I forgot to change the name of the silkscreen) for 1s also brings you back. \nIf you ever get stuck, just press the reset button.\n");
        ch1_done    = true;
        ch1_waiting = false;
        return false;
    }

    ch1_print_question(ch1_q);
    return false;
}

/* ── Mic challenge description (CH2) ─────────────────────────── */
/* Description only. The live signal analysis runs on a dedicated mic station
 * at the front of the stage (standalone firmware), and the real flag lives on
 * the organizer badge there. */

void setupCH2(void)
{
    printf("\n==========================\n");
    printf("  CHALLENGE 2\n");
    printf("  Music to My Ear\n");
    printf("==========================\n");
    printf("I love music, but my ears only tingle for the highest notes.\n\n");
    printf("Head to the mic station at the front.\n");
    printf("\nPress [0] to return to menu.\n");
}

/* ── eFuse description (CH3) ────────────────────────────────── */

void setupCH3(void)
{
    printf("\n==========================\n");
    printf("  CHALLENGE 3\n");
    printf("  Hidden in Plain Sight\n");
    printf("==========================\n");
    printf("If your look VERY closely at your badge, you can read the flag.\n");
    printf("Wrap the hex value as:  grey{0x<value>}\n\n");
    printf("\nPress [0] to return to menu.\n");
}

/* ── Thread description (CH4) ───────────────────────────────── */

void setupCH4(void)
{
    printf("\n================================\n");
    printf("  CHALLENGE 4\n");
    printf("  What's this Thread Connecting Us?\n");
    printf("================================\n");
    printf("  GreyFlag IoT badge\n");
    printf("  Our brand-new IoT platform.\n");
    printf("  Joiner credential: GREYFLAG99\n");
    printf("================================\n\n");
    printf("You are now at the OpenThread CLI.\n");
    printf("Find your way onto the GreyFlag network.\n\n");
    printf("Type 'exit' or 'menu' (or long-press the button) to leave.\n\n");
    printf("> ");
    fflush(stdout);
}
