from rest_framework import status
from rest_framework.authtoken.admin import User

from rest_framework.authtoken.models import Token

from rest_framework.test import APITestCase

from .models import Flashcard, Category, FlashcardsSet


class FlashcardTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user("tester", "Wy w ciemnościach – reflektory chronią was")
        self.another_user = User.objects.create_user("tester2", "Oświetlając tylko scenę, na niej mnie!")
        self.token = Token.objects.get(user__username='tester')
        self.another_token = Token.objects.get(user__username='tester2')
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        category = Category.objects.create(name="test", level="easy")
        self.flashcards_set = FlashcardsSet.objects.create(
            name="testowy",
            author=self.user,
            category=category
        )

        self.valid_flashcard = {
            "front": "Jak na dłoni widać mą stężałą twarz",
            "back": "Gdy przez mrok próbują oczy przebić się!",
            "flashcard_set": self.flashcards_set.id,
            "author": self.user,
        }

        self.invalid_flashcard = {
            "front": "Ktoś mi tutaj może powie, że już charczę,",
            "back": "Że już nie rozróżniam poszczególnych słów,",
            "flashcard_set": '',
            "author": self.user,
        }
        self.url = "/api/flashcards/"

    def test_create_valid_flashcard(self):
        response = self.client.post(self.url, self.valid_flashcard)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flashcard.objects.count(), 1)
        self.assertEqual(Flashcard.objects.get().front, "Jak na dłoni widać mą stężałą twarz")

    def test_create_invalid_flashcard(self):
        response = self.client.post(self.url, self.invalid_flashcard)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_flashcards_created_by_user(self):
        self.client.post(self.url, self.valid_flashcard)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get('id'), 1)
        self.assertEqual(response.data[0].get('front'), "Jak na dłoni widać mą stężałą twarz")

    def test_flashcard_exists_already(self):
        self.client.post(self.url, self.valid_flashcard)
        response = self.client.post(self.url, self.valid_flashcard)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_flashcard_from_given_dataset(self):
        self.client.post(self.url, self.valid_flashcard)
        response = self.client.get(self.url + f"?flashcard_set={self.flashcards_set.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("id"), 1)
        self.assertEqual(response.data[0].get('front'), "Jak na dłoni widać mą stężałą twarz")

    def test_delete_flashcard_of_given_id(self):
        self.client.post(self.url, self.valid_flashcard)
        response = self.client.delete(self.url + "1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # potwierdzenie, że fiszka została usunięta
        response = self.client.delete(self.url + "1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_flashcard_of_given_id_by_another_user(self):
        self.client.post(self.url, self.valid_flashcard)
        self.client.force_authenticate(user=self.another_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.another_token.key)
        response = self.client.delete(self.url + "1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_flashcard_of_given_id(self):
        self.client.post(self.url, self.valid_flashcard)
        response = self.client.get(self.url + "?flashcard_id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("id"), 1)
        self.assertEqual(response.data[0].get('front'), "Jak na dłoni widać mą stężałą twarz")

    def test_edit_flashcard_of_given_id(self):
        self.client.post(self.url, self.valid_flashcard)
        self.valid_flashcard["front"] = "Nowych chwytów na gitarze nie wyćwiczę"
        response = self.client.patch(self.url + "1/", self.valid_flashcard)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), 1)
        self.assertEqual(response.data.get('front'), "Nowych chwytów na gitarze nie wyćwiczę")


class FlashcardsSetTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", "Wy w ciemnościach – reflektory chronią was")
        self.token = Token.objects.get(user__username='tester')
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.category = Category.objects.create(name="test", level="easy")

        self.valid_flashcards_set = {
            "name": "ze sceny [niebieska karta remix]",
            "author": self.user,
            "category": self.category.id
        }

        self.invalid_flashcards_set = {
            "name": "ze sceny [niebieska karta remix]",
            "author": self.user,
            "category": self.category.name
        }

        self.url = "/api/sets/"

    def test_add_valid_flashcards_set(self):
        response = self.client.post(self.url, self.valid_flashcards_set)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get("id"), 1)
        self.assertEqual(response.data.get("name"), "ze sceny [niebieska karta remix]")

    def test_add_invalid_flashcards_set(self):
        response = self.client.post(self.url, self.invalid_flashcards_set)
        self.assertEqual(response.status_code, 400)

    def test_get_flashcardset_of_given_id(self):
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.get(self.url + "?flashcard_set_id=1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("id"), 1)
        self.assertEqual(response.data[0].get('name'), "ze sceny [niebieska karta remix]")

    def test_flashcards_set_exists_for_user_and_not_created(self):
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.post(self.url, self.valid_flashcards_set)
        self.assertEqual(response.status_code, 400)

    def test_flashcards_set_exists_not_for_same_user_and_created(self):
        self.client.post(self.url, self.valid_flashcards_set)
        second_user = User.objects.create_user("tester2", "Wy w ciemnościach – reflektory chronią was")
        token = Token.objects.get(user__username='tester2')
        self.client.force_authenticate(user=second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.url, self.valid_flashcards_set)
        self.assertEqual(response.status_code, 201)

    def test_get_only_public_flashcards_set(self):
        self.valid_flashcards_set["status"] = "private"
        self.client.post(self.url, self.valid_flashcards_set)
        second_user = User.objects.create_user("tester2", "Wy w ciemnościach – reflektory chronią was")
        token = Token.objects.get(user__username='tester2')
        self.client.force_authenticate(user=second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.valid_flashcards_set["status"] = "public"
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(len(response.data), 2)

    def test_get_only_public_and_user_flashcards_set(self):
        self.valid_flashcards_set["status"] = "private"
        self.client.post(self.url, self.valid_flashcards_set)
        second_user = User.objects.create_user("tester2", "Wy w ciemnościach – reflektory chronią was")
        token = Token.objects.get(user__username='tester2')
        self.client.force_authenticate(user=second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.valid_flashcards_set["status"] = "public"
        self.client.post(self.url, self.valid_flashcards_set)
        self.valid_flashcards_set["status"] = "private"
        self.valid_flashcards_set["name"] = "ze sceny [niebieska karta remix] 2"
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("name"), "ze sceny [niebieska karta remix]")
        self.assertEqual(response.data[1].get("name"), "ze sceny [niebieska karta remix] 2")

    def test_delete_flashcardset_of_given_id(self):
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.delete(self.url + "1/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        # potwierdzenie, że zestaw został usunięty
        response = self.client.delete(self.url + "1/")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_edit_flashcardset_of_given_id(self):
        self.client.post(self.url, self.valid_flashcards_set)
        self.valid_flashcards_set["name"] = "ze sceny [karta remix]"
        response = self.client.patch(self.url + "1/", self.valid_flashcards_set)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get("id"), 1)
        self.assertEqual(response.data.get('name'), "ze sceny [karta remix]")

    def test_get_flashcard_from_given_category(self):
        self.client.post(self.url, self.valid_flashcards_set)
        # tworzymy nową kategorię, by sprawdzić, czy tylko jedna fiszka zostanie wybrana
        another_category = Category.objects.create(name="test2", level="easy")
        self.valid_flashcards_set["category"] = another_category.id
        self.client.post(self.url, self.valid_flashcards_set)
        response = self.client.get(self.url + f"?category={self.category.name}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("id"), 1)
        self.assertEqual(response.data[0].get('name'), "ze sceny [niebieska karta remix]")

    def test_get_only_given_user_public_flashcards_set(self):
        second_user = User.objects.create_user("tester2", "Wy w ciemnościach – reflektory chronią was")
        token = Token.objects.get(user__username='tester2')
        self.client.force_authenticate(user=second_user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.valid_flashcards_set["status"] = "public"
        self.valid_flashcards_set["name"] = "publiczny zestaw"
        self.client.post(self.url, self.valid_flashcards_set)

        self.valid_flashcards_set["status"] = "private"
        self.valid_flashcards_set["name"] = "prywatny zestaw"
        self.client.post(self.url, self.valid_flashcards_set)

        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        response = self.client.get(self.url + "?author=tester2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0].get("name"), "publiczny zestaw")


class RatingTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user("tester", "Wy w ciemnościach – reflektory chronią was")
        self.token = Token.objects.get(user__username='tester')
        self.client.force_authenticate(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        category = Category.objects.create(name="test", level="easy")
        self.flashcards_set = FlashcardsSet.objects.create(
            name="testowy",
            author=self.user,
            category=category
        )

        self.valid_rating = {
            "set": self.flashcards_set.id,
            "user": self.user,
            "rate": 5
        }

        self.invalid_rating = {
            "set": self.flashcards_set.id,
            "user": self.user,
            "rate": -5
        }

        self.url = f"/api/ratings/"

    def test_create_correct_rating(self):
        response = self.client.post(self.url, self.valid_rating)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data.get("message"), "Ocena została dodana!")

    def test_create_incorrect_rating(self):
        response = self.client.post(self.url, self.invalid_rating)
        self.assertEqual(response.status_code, 400)

    def test_create_same_rating_twice(self):
        self.client.post(self.url, self.valid_rating)
        response = self.client.post(self.url, self.valid_rating)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data.get("detail"), "Już zagłosowałeś na ten zestaw.")

    def test_get_rating_for_flashcard_set(self):
        self.client.post(self.url, self.valid_rating)
        response = self.client.get(self.url, {"flashcard_set": self.flashcards_set.name})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)


