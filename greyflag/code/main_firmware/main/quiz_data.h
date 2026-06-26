#pragma once
/*
 * ============================================================================
 *  GREYFLAG QUIZ PLANNER  —  Challenge 1 "Welcome to GreyFlag"
 * ============================================================================
 *  ✏️  EDIT THIS FILE to customise the MCQ. Each question is one { ... } block.
 *
 *  Per question:
 *    .question       The question text (no need to number it).
 *    .options        Exactly 4 answers. Do NOT prefix them with "a)"/"b)" —
 *                    the badge prints the a/b/c/d labels automatically.
 *    .answer         The correct letter: 'a', 'b', 'c', or 'd'.
 *    .reply_correct  Message shown when they answer correctly.
 *                    Leave as "" to fall back to the default "Correct!".
 *    .reply_wrong    Message shown when they answer wrong (the quiz then
 *                    restarts from question 1). Leave "" for the default.
 *
 *  • Add or remove blocks freely — the question count is auto-detected.
 *  • QUIZ_FLAG below is printed once ALL questions are answered correctly.
 * ============================================================================
 */

#define QUIZ_FLAG  "grey{my_baby_steps}"

typedef struct {
    const char *question;
    const char *options[4];
    char        answer;
    const char *reply_correct;
    const char *reply_wrong;
} mcq_t;

static const mcq_t quiz[] = {
    {
        .question = "What microcontroller is on this badge?",
        .options  = {"ESP32", "ESP32-C6", "ESP8266", "ESP32-S3"},
        .answer   = 'b',
        .reply_correct = "Correct! The C6 means it is cheap while the S series is for powerful systems. \nThe H series is exclusively for IoT and doesn't have Wi-Fi. \nThe WROOM means it contains other things on the chip like antennas \nand this chip specifically has 8MB of flash.",
        .reply_wrong   = "Look at the back of the badge — it's printed on the chip.",
    },
    {
        .question = "What is the onboard power source that keeps it portable?",
        .options  = {"AAA batteries", "Coin cells", "LiPo battery", "Magic"},
        .answer   = 'c',
        .reply_correct = "Correct! LiPos are rechargeable and keep it portable. \nUnfortunately, they are not included in the kit...",
        .reply_wrong   = "Look behind, there's an empty holder with a small label on the silkscreen beside it.",
    },
    {
        .question = "Which digital audio interface does this badge use?",
        .options  = {"SPI", "I2C", "UART", "I2S"},
        .answer   = 'd',
        .reply_correct = "Correct! I2S is THE protocol that embedded devices use to drive audio peripherals.",
        .reply_wrong   = "These are all protocols commonly found in embedded devices. Do a quick google search.",
    },
    {
        .question = "How many LEDs are on this badge?",
        .options  = {"3", "4", "5", "6"},
        .answer   = 'c',
        .reply_correct = "Correct! 5 LEDs you can play with in LED Modes.",
        .reply_wrong   = "Look at the front of the badge.",
    },
    {
        .question = "Which 802.15.4-based mesh protocol does the ESP32-C6 support natively?",
        .options  = {"Zigbee", "WiFi", "Thread", "Literally Everything"},
        .answer   = 'd',
        .reply_correct = "Correct! Yep, the ESP32-C6 is crazy and supports most common wireless protocols including Wi-Fi, Zigbee, Matter, ESP-NOW. \nAlso, this Thread may be the key to a later challenge...",
        .reply_wrong   = "How did you even get here?",
    },
};
#define QUIZ_LEN (sizeof(quiz) / sizeof(quiz[0]))
