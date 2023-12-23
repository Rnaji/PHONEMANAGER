class NonOledDiagnostic:
    GRADE_A = "GRADE A"
    GRADE_B = "GRADE B"
    GRADE_C = "GRADE C"
    GRADE_D = "GRADE D"
    GRADE_E = "GRADE E"
    GRADE_F = "GRADE F"
    GRADE_G = "GRADE G"
    GRADE_AFTERMARKET = "GRADE AFTERMARKET"
    GRADE_POUBELLE = "GRADE POUBELLE"
    GRADE_HS = "GRADE HS"

    def __init__(self):
        self.grade = None

    def run_diagnostic(self):
        print("Commencer le diagnostic...")
        self.grade = self.grade_diagnostic()
        print("Résultat du diagnostic :", self.grade)

    def grade_diagnostic(self):
        answers = self.get_user_answers()

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_A

        if (
            answers[0] == "non" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_AFTERMARKET

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "oui" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_B

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "oui" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_B

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "oui" and
            answers[5] == "non" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_G

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "oui" and
            answers[6] == "non" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_D

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "oui" and
            answers[7] == "non" and
            answers[8] == "non"
        ):
            return self.GRADE_B

        if (
            "oui" in answers or
            "oui" in answers[1:]  # Check si au moins une des réponses après la première est "oui"
        ):
            return self.GRADE_POUBELLE

        if (
            answers[0] == "oui" and
            answers[1] == "non" and
            answers[2] == "non" and
            answers[3] == "non" and
            answers[4] == "non" and
            answers[5] == "non" and
            answers[6] == "oui" and
            answers[7] == "oui" and
            answers[8] == "non"
        ):
            return self.GRADE_C

        return self.GRADE_HS

    def get_user_answers(self):
        answers = []
        for i in range(1, 10):
            answer = input(f"({i}) {self.get_question_text(i)} ").lower()
            answers.append(answer)
        return answers

    def get_question_text(self, question_number):
        questions = {
            1: "L’écran est original (oui/non) ?",
            2: "L’écran présente des dommages fonctionnels (oui/non) ?",
            3: "L’écran a des problèmes de rétroéclairage (oui/non) ?",
            4: "L’écran est jaunâtre (oui/non) ?",
            5: "L’écran a des pixels morts (oui/non) ?",
            6: "Le tactile est défectueux (oui/non) ?",
            7: "Le 3D Touch est défectueux (oui/non) ?",
            8: "L’écran a des points lumineux ou une distorsion des couleurs (oui/non) ?",
            9: "L’écran a des Gros pixels morts (oui/non) ?"
        }
        return questions[question_number]

    def get_questions(self):
        return [
            {"qid": 1, "text": self.get_question_text(1)},
            {"qid": 2, "text": self.get_question_text(2)},
            {"qid": 3, "text": self.get_question_text(3)},
            {"qid": 4, "text": self.get_question_text(4)},
            {"qid": 5, "text": self.get_question_text(5)},
            {"qid": 6, "text": self.get_question_text(6)},
            {"qid": 7, "text": self.get_question_text(7)},
            {"qid": 8, "text": self.get_question_text(8)},
            {"qid": 9, "text": self.get_question_text(9)},
        ]

if __name__ == "__main__":
    diagnostic = NonOledDiagnostic()
    diagnostic.run_diagnostic()
