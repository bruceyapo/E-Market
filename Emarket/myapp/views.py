import pickle
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render,redirect
from django.views.decorators.http import require_POST
import numpy as np

from authentifications.forms import GestStockUpdateForm, VendeurUpdateForm
from authentifications.models import Adminitrateur, GesteionnaireStock, Utilisateur, Vendeur, client
from boutique.models import Produit, Stock
from categorie.models import CategorieProduit
from commande.models import Order, OrderProduct
from .forms import AjoutCategorieForm, AjoutProduitForm, DateForm, PredictionForm, StockUpdateForm, UploadFileForm,ClientForm, VenteForm, VerifClientForm
from .models import Notification, Recu, Vente
from django.contrib.auth import authenticate, login, logout
from django.template.loader import render_to_string
import pdfkit
from reportlab.pdfgen import canvas
from django.db.models import Sum, Count,F
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
import csv
from django.db.models import QuerySet
import pandas as pd
from django.forms import inlineformset_factory
from django.utils import timezone
from django.db.models.functions import ExtractMonth, ExtractYear, Cast
from django.db.models.fields import DateField
from datetime import datetime,timedelta

# Importer les bibliothèques
from pandas.tseries.offsets import DateOffset
from prophet import Prophet
# from sklearn.metrics import mean_absolute_error, mean_squared_error
import pyodbc
import pickle
import os
import calendar
import logging

# Configurer le niveau de logging de cmdstanpy pour ignorer les messages d'information
logging.getLogger('cmdstanpy').setLevel(logging.ERROR)


@login_required(login_url='connexion')
def liste_vendeur(request):
    vendeurs = Vendeur.objects.all().select_related('IdUtilisateur')
    nombre_total_vendeur = vendeurs.count()
    paginator = Paginator(vendeurs, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    vendeurs = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_vendeur.html',locals())

def supprimer_vendeur(request, vendeur_id):
    vendeur = Vendeur.objects.get(id=vendeur_id)
    vendeur.delete()
    messages.success(request, f'Le Vendeur {vendeur.nom} a été supprimée avec succès.')
    return redirect('liste_vendeur')

@login_required(login_url='connexion')
def modif_vendeur(request, vendeur_id):
    vendeur = get_object_or_404(Vendeur, pk=vendeur_id)
    if request.method == 'POST':
        form = VendeurUpdateForm(request.POST, request.FILES, instance=vendeur)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Utilisateur.objects.filter(email=email).exists():
                messages.warning(request, "Un utilisateur avec cet email existe déjà.")
                return render(request, 'app/authentification/modif_vendeur.html', {'form': form})
            elif form.is_valid():
                form.save()
                messages.success(request, 'Les informations du vendeur ont été mises à jour avec succès.')
                return redirect('liste_vendeur')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = VendeurUpdateForm(instance=vendeur)
    return render(request, 'app/authentification/modif_vendeur.html', {'form': form,'vendeur': vendeur})


@login_required(login_url='connexion')
def liste_client(request):
    clients = client.objects.all()
    nombre_total_client = clients.count()
    paginator = Paginator(clients, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    clients = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_client.html',locals())


def liste_produit_categorie(request):
    # liste des produits
    produits = Produit.objects.all().select_related('IdCategorie')
    nombre_total_produit = produits.count()
    paginator = Paginator(produits, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    produits = paginator.get_page(page_number)
    
    # liste des categories de produit
    categories_produit = CategorieProduit.objects.all()
    nombre_total_categorie_produit = categories_produit.count()
    paginator = Paginator(categories_produit, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    categories_produit = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_produit.html',locals())

@login_required(login_url='connexion')
def AjoutCategoriet(request):
    # if request.method == 'POST':
    form = AjoutCategorieForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,"Categorie produit enregistré avec success")
        form = AjoutCategorieForm()
        return redirect('liste_produit_categorie')
        # Redirection ou autres actions
    else:
        form = AjoutCategorieForm()
    return render(request, 'app/admin/AjoutCategoriet.html', {'form': form})

def supprimer_categorie(request, categorie_id):
    Categorie = CategorieProduit.objects.get(id=categorie_id)
    Categorie.delete()
    messages.success(request, f'La Categorie {Categorie.nom} a été supprimée avec succès.')
    return redirect('liste_produit_categorie')

@login_required(login_url='connexion')
def modif_categorie(request, categorie_id):
    categorie = get_object_or_404(CategorieProduit, pk=categorie_id)  # Assurez-vous que le vendeur appartient à l'utilisateur connecté
    form = AjoutCategorieForm(request.POST or None, instance=categorie)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f"La categorie {categorie.nom} ont été mises à jour avec succès.")
            return redirect('liste_produit_categorie')  # Remplacez 'liste_vendeur' par le nom réel de votre vue qui affiche la liste des vendeurs
    else:
        # Le formulaire est pré-rempli avec les informations existantes du vendeur
        form = AjoutCategorieForm(instance=categorie)
    return render(request, 'app/admin/modif_categorie.html', {'form': form, 'categorie': categorie})

@login_required(login_url='connexion')
def AjoutProduit(request):
    # if request.method == 'POST':
    form = AjoutProduitForm(request.POST)
    if form.is_valid():
        form.save()
        messages.success(request,"Produit enregistré avec success")
        form = AjoutProduitForm()
        return redirect('liste_produit_categorie')
        # Redirection ou autres actions
    else:
        form = AjoutProduitForm()
    return render(request, 'app/admin/AjoutProduit.html', {'form': form})


@login_required(login_url='connexion')
def modif_produit(request, produit_id):
    produit = get_object_or_404(Produit, pk=produit_id,)  # Assurez-vous que le vendeur appartient à l'utilisateur connecté
    form = AjoutProduitForm(request.POST or None, instance=produit)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, "Produit a été mises à jour avec succès.")
            return redirect('liste_produit_categorie')  # Remplacez 'liste_vendeur' par le nom réel de votre vue qui affiche la liste des vendeurs
    else:
        # Le formulaire est pré-rempli avec les informations existantes du vendeur
        form = AjoutProduitForm(instance=produit)
    return render(request, 'app/admin/modif_produit.html', {'form': form, 'produit': produit})

def supprimer_produit(request, produit_id):
    produit = Produit.objects.get(id=produit_id)
    produit.delete()
    messages.success(request, f'Le produit {produit.Nom} a été supprimée avec succès.')
    return redirect('liste_produit_categorie')


def liste_geststock(request):
    GestStocks = GesteionnaireStock.objects.all().select_related('IdUtilisateur')
    nombre_total_GestStock = GestStocks.count()
    paginator = Paginator(GestStocks, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    GestStocks = paginator.get_page(page_number)
    return render(request, 'app/admin/liste_geststock.html',locals())

def pipeline(df):
    # copie du dataset
    # df=data.copy()
    df = df.rename(columns={'Nom': 'Produit','PrixUnitaire': 'Prix'})
    # Convertir la colonne "Prix" en float
    df['Prix'] = df['Prix'].astype(float)
    # Convertir la colonne "Date" en datetime
    df['Date'] = pd.to_datetime(df['Date'])
    # Extraire le mois et l'année de chaque date
    df['Mois'] = df['Date'].dt.month
    df['Année'] = df['Date'].dt.year
    # Calculer le chiffre d'affaires par produit pour chaque mois
    df = df.groupby(['Produit', 'Année', 'Mois']).agg({'Prix': ['count', 'sum', 'mean']})
    df.columns = ['Nombre de ventes', 'CA', 'Prix Unitaire']
    df = df.reset_index()
    # vente par annee pour chaque produit
    ventes_par_annee = df.groupby(['Produit', 'Année']).agg({'Nombre de ventes': 'sum', 'CA': 'sum'}).reset_index()
    # Calculer le nombre d'années de vente pour chaque produit
    annees_vente_par_produit = ventes_par_annee.groupby('Produit')['Année'].nunique().reset_index()
    # Calculer la somme des ventes et du chiffre d'affaires pour chaque produit
    somme_ventes_ca_par_produit = ventes_par_annee.groupby('Produit').agg({'Nombre de ventes': 'sum', 'CA': 'sum'}).reset_index()
    # Fusionner les DataFrames pour obtenir le nombre d'années de vente, la somme des ventes et la somme du chiffre d'affaires par produit
    merged_df = pd.merge(annees_vente_par_produit, somme_ventes_ca_par_produit, on='Produit')
    # Déterminer l'année maximale dans le DataFrame
    annee_maximale = merged_df['Année'].max()

    # Diviser la colonne "Nombre de ventes" par l'année maximale
    merged_df['Nombre de ventes normalisé'] = merged_df['Nombre de ventes'] / annee_maximale
    # Diviser la colonne "CA" par l'année maximale
    merged_df['CA normalisé'] = merged_df['CA'] / annee_maximale
    # Supprimer les colonnes normalisées si elles existent déjà
    merged_df.drop(['Nombre de ventes', 'CA'], axis=1, errors='ignore', inplace=True)
    # selection des produits superieurs au 3em quartille
    merged_df=merged_df[merged_df["Nombre de ventes normalisé"]>2.5]
    # Trier le dataframe par 'Nombre de ventes normalisé' puis par 'CA normalisé' en cas d'égalité
    top_10_produits = merged_df.sort_values(by=['Nombre de ventes normalisé', 'CA normalisé'], ascending=False)
    # Afficher le top 10 des produits
    top_10_produits
    # Obtenir une liste des produits uniques
    produits_uniques = top_10_produits["Produit"].unique()
    # Identifier les éléments de la liste des produits uniques dans le DataFrame
    df = df[df['Produit'].isin(produits_uniques)]
    # Créer une colonne "Date"
    df["Date"] = pd.to_datetime(df["Année"].astype(str) + "-" + df["Mois"].astype(str))

    # Supprimer les colonnes Année et Mois car elles ne sont plus nécessaires
    df.drop(columns=['Année', 'Mois'], inplace=True)

    # Trier les données par date
    df = df.sort_values('Date')
    # Trouver la date minimale et maximale
    
    return df


def data_set():   
    server = 'DESKTOP-QQGKONI\\SQLEXPRESS'
    database = 'Emarket_app'
    username = 'Yapo2000'
    password = 'Yapo2000@'
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};\
                        SERVER='+server+';\
                        DATABASE='+database+';\
                        UID='+username+';\
                        PWD='+password+';\
                        Trusted_Connection=yes;')

    cursor = conn.cursor()
    Vente = 'myapp_vente'
    Produit = 'boutique_produit'

    group_query = f'''SELECT CONVERT(VARCHAR(255), V.DateVente) AS Date, P.Nom, P.PrixUnitaire FROM {Vente} V JOIN {Produit} P ON V.IdProduit_id = P.id '''
    data = pd.read_sql(group_query, conn)
    df = pipeline(data).copy()
    sous_dataframes = {}
    for produit, sous_df in df.groupby('Produit'):
        sous_dataframes[produit] = sous_df
    # sous_dataframes

    # Définir les dates minimale et maximale
    # date_min = pd.to_datetime("2021-02-01")
    # date_max = pd.to_datetime("2024-01-01")
    date_min = df['Date'].min()
    date_max = df['Date'].max()
    # Créer une liste de dates
    dates = pd.date_range(start=date_min, end=date_max, freq='D').to_list()

    # Créer un dictionnaire avec les dates
    dict_dates = {"Date": dates}

    # Convertir le dictionnaire en dataframe
    df_dates = pd.DataFrame(dict_dates)
    return sous_dataframes, df_dates

def predict_sales_for_month(year, month, model, sous_df):
    days_in_month = calendar.monthrange(year, month)[1]
    start_date = f'{year}-{month:02d}-01'
    end_date = f'{year}-{month:02d}-{days_in_month}'
    future_dates = pd.date_range(start=start_date, end=end_date, freq='D')
    future = pd.DataFrame({'ds': future_dates})
    forecast = model.predict(future)
    prix_unitaire = sous_df["Prix Unitaire"].median()
    total_sales = round(forecast['yhat'].sum())
    chiffre_affaires = total_sales * prix_unitaire
    return total_sales, chiffre_affaires

# def prediction(request):
#     resultats = []
#     if request.method == 'POST':
#         form = PredictionForm(request.POST)
#         if form.is_valid():
#             year = int(form.cleaned_data['year'])
#             month = int(form.cleaned_data['month'])
#             sous_dataframes, df_dates = data_set()
#             # Initialiser un dictionnaire pour stocker les résultats
#             for produit, sous_df in sous_dataframes.items():
#                 sous_df.reset_index(drop=True, inplace=True)
#                 df_surechantillonne = df_dates.merge(sous_df, how='left', on='Date')
#                 df_surechantillonne['Nombre de ventes'].fillna(0, inplace=True)
#                 df_surechantillonne['CA'].fillna(0, inplace=True)
#                 df_surechantillonne["Prix Unitaire"].replace(np.nan, sous_df["Prix Unitaire"].median(), inplace=True)
#                 df_surechantillonne["Produit"].replace(np.nan, f"{produit}", inplace=True)

#                 df_prophet = df_surechantillonne.copy()
#                 df_prophet['ds'] = df_prophet['Date']
#                 df_prophet['y'] = df_prophet['Nombre de ventes']

#                 model = Prophet()
#                 model.fit(df_prophet)

#                 model_filename = f'models/predict_{produit}.pkl'
                
#                 if os.path.exists(model_filename):
#                     print(f"Le modèle {produit} existe déjà. Mise à jour du modèle.")
#                 else:
#                     print(f"Le modèle {produit} n'existe pas. Création d'un nouveau modèle.")
                
#                 # Enregistrer le modèle
#                 with open(model_filename, 'wb') as f:
#                     pickle.dump(model, f)
#                 print(f"Le Modèle {produit} est enregistré sous le nom '{model_filename}'")
                
#                 # year = 2030
#                 # month = 9
#                 with open(f'models/predict_{produit}.pkl', 'rb') as f:
#                     model = pickle.load(f)
#                 total_sales, chiffre_affaires = predict_sales_for_month(year, month, model, sous_df)
#                 resultats.append((produit, total_sales, chiffre_affaires))
#             # Convertir les résultats en DataFrame
#             resultats_df = pd.DataFrame(resultats, columns=['Produit', 'Nbre_de_ventes_predites', 'Chiffre_affaires_predit'])

#             # Trier les résultats par Nombre de ventes prédites et sélectionner les 10 meilleurs produits
#             top_10_resultats = resultats_df.sort_values(by='Nbre_de_ventes_predites', ascending=False).head(10)
#             return render(request, 'app/admin/prediction.html',locals())
#     else:
#         form = PredictionForm()

#     return render(request, 'app/admin/prediction.html',locals())

def prediction(request):
    resultats = []
    if request.method == 'POST':
        form = PredictionForm(request.POST)
        if form.is_valid():
            year = int(form.cleaned_data['year'])
            month = int(form.cleaned_data['month'])
            month_name = calendar.month_name[month]
            days_in_month = calendar.monthrange(year, month)[1]
            # {calendar.month_name[month]} {year}
            sous_dataframes, df_dates = data_set()
            
            for produit, sous_df in sous_dataframes.items():
                sous_df.reset_index(drop=True, inplace=True)
                df_surechantillonne = df_dates.merge(sous_df, how='left', on='Date')
                df_surechantillonne = df_surechantillonne.fillna({
                    'Nombre de ventes': 0,
                    'CA': 0,
                    'Prix Unitaire': sous_df["Prix Unitaire"].median(),
                    'Produit': produit
                })

                df_prophet = df_surechantillonne.copy()
                df_prophet['ds'] = df_prophet['Date']
                df_prophet['y'] = df_prophet['Nombre de ventes']

                model = Prophet()
                model.fit(df_prophet)

                model_filename = f'models/predict_{produit}.pkl'
                
                if os.path.exists(model_filename):
                    print(f"Le modèle {produit} existe déjà. Mise à jour du modèle.")
                else:
                    print(f"Le modèle {produit} n'existe pas. Création d'un nouveau modèle.")
                
                # Enregistrer le modèle
                with open(model_filename, 'wb') as f:
                    pickle.dump(model, f)
                # print(f"Le Modèle {produit} est enregistré sous le nom '{model_filename}'")
                
                with open(f'models/predict_{produit}.pkl', 'rb') as f:
                    model = pickle.load(f)
                total_sales, chiffre_affaires = predict_sales_for_month(year, month, model, sous_df)
                resultats.append((produit, total_sales, chiffre_affaires))
            
            # Convertir les résultats en DataFrame
            resultats_df = pd.DataFrame(resultats, columns=['Produit', 'Nbre_de_ventes_predites', 'Chiffre_affaires_predit'])

            # Trier les résultats par Nombre de ventes prédites et sélectionner les 10 meilleurs produits
            top_10_resultats = resultats_df.sort_values(by='Nbre_de_ventes_predites', ascending=False).head(10)
            
            # Préparer les données pour Chart.js
            produits = top_10_resultats['Produit'].tolist()
            ventes = top_10_resultats['Nbre_de_ventes_predites'].tolist()
            ca = top_10_resultats['Chiffre_affaires_predit'].tolist()
            
            context = {
                'form': form,
                'month_name': month_name,
                'produits':produits,
                'ventes':ventes,
                'ca':ca,
                'year': year,
                'month': month,
                'top_10_resultats': top_10_resultats
                }
            return render(request, 'app/admin/prediction.html', context)
    else:
        form = PredictionForm()

    return render(request, 'app/admin/prediction.html', {'form': form})
# def predict_sales_for_month(year, month, model):
#     future = model.make_future_dataframe(periods=30)
#     forecast = model.predict(future)
#     # Filtrer pour le mois et l'année spécifiques
#     forecast['ds'] = pd.to_datetime(forecast['ds'])
#     forecast_month = forecast[(forecast['ds'].dt.year == year) & (forecast['ds'].dt.month == month)]
#     total_sales = forecast_month['yhat'].sum()
#     chiffre_affaires = (forecast_month['yhat'] * forecast_month['prix']).sum()  # Assurez-vous que la colonne 'prix' est dans votre DataFrame
#     return total_sales, chiffre_affaires

# def prediction(request):
#     # Charger les modèles et faire des prédictions
#     resultats = []
#     produits = Vente.objects.values_list('IdProduit__Nom', flat=True).distinct()
    
#     for produit in produits:
#         try:
#             with open(f'models/prophet_model_{produit}.pkl', 'rb') as f:
#                 model = pickle.load(f)
#             total_sales, chiffre_affaires = predict_sales_for_month(2024, 1, model)
#             resultats.append((produit, total_sales, chiffre_affaires))
#         except FileNotFoundError:
#             continue

#     resultats_df = pd.DataFrame(resultats, columns=['Produit', 'Nombre_ventes_prédites', 'Chiffre_affaires'])
#     top_10_resultats = resultats_df.sort_values(by='Nombre_ventes_prédites', ascending=False).head(10)
#     return render(request, 'app/admin/prediction.html',locals())

@login_required(login_url='connexion')
def modif_geststock(request, geststock_id):
    geststock = get_object_or_404(GesteionnaireStock, pk=geststock_id)
    if request.method == 'POST':
        form = GestStockUpdateForm(request.POST, request.FILES, instance=geststock)
        if form.is_valid():
            email = form.cleaned_data['email']
            if Utilisateur.objects.filter(email=email).exists():
                messages.warning(request, "Un utilisateur avec cet email existe déjà.")
                return render(request, 'app/authentification/modif_geststock.html', {'form': form})
            elif form.is_valid():
                form.save()
                messages.success(request, 'Les informations du gestionnaire de stock ont été mises à jour avec succès.')
                return redirect('liste_geststock')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = GestStockUpdateForm(instance=geststock)
    return render(request, 'app/authentification/modif_geststock.html', {'form': form,'geststock': geststock})

def supprimer_geststock(request, geststock_id):
    geststock = GesteionnaireStock.objects.get(id=geststock_id)
    geststock.delete()
    messages.success(request, f'Le Gesteionnaire de Stock {geststock.nom} a été supprimée avec succès.')
    return redirect('liste_geststock')



# Fonction de vue de connexion
def format_number(num):
    if num :
        if num >= 1000000:
            return f"{num / 1000000:.1f}M+"
        if num >= 1000:
            return f"{num / 1000:.1f}K+"
        return str(num)
    else:
        return 0

# @login_required(login_url='connexion')
# def visuels(request):
#     user = request.user
#     utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#         # Utiliser la clé étrangère pour récupérer l'administrateur associé
#     administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
#     # Si le formulaire a été soumis
    
#     date_form = DateForm(request.GET)
#     if date_form.is_valid():
#         selected_date_str = date_form.cleaned_data['date_input']
#         # Convertir la chaîne de caractères en date
#         selected_date = datetime.strptime(selected_date_str, '%m/%Y')
#         year = selected_date.year
#         month = selected_date.month
#         # Filtrer les ventes pour le mois et l'année sélectionnés
#         ventes_for_date = Vente.objects.annotate(
#             year=ExtractYear('DateVente'),
#             month=ExtractMonth('DateVente')
#         ).filter(year=year, month=month)
        
        
#         # Meilleur produit vendu
#         # Ensuite, vous pouvez effectuer votre agrégation pour obtenir le meilleur produit vendu
#         # best_product = Vente.objects.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold').first()
#         # Ensuite, vous pouvez obtenir les cinq meilleurs produits vendus
        
#         # Récupérer les 5 meilleurs produits par quantité vendue
#         top_5_products = ventes_for_date.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold')[:5]

#         # top_products = ventes_for_date.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold')[:5]

#         # Meilleur employé
#         best_employee = Vente.objects.filter(DateVente__year=year, DateVente__month=month).values('IdVendeur__nom', 'IdVendeur__prenoms').annotate(total_sales=Sum('MontantTotal')).order_by('-total_sales').first()

#         # Top 5 des meilleurs clients
#         top_clients = Vente.objects.filter(DateVente__year=year, DateVente__month=month).values('IdClient__nom', 'IdClient__prenoms').annotate(total_purchases=Count('IdClient')).order_by('-total_purchases')[:5]
        
#         # Agrégation pour obtenir le nombre total de ventes par mois/année
#         sales_by_date = Vente.objects.filter(DateVente__year=year, DateVente__month=month).annotate(
#             month=ExtractMonth('DateVente'),
#             year=ExtractYear('DateVente')
#         ).values('year', 'month').annotate(
#             total_sales=Count('id'),
#         ).order_by('year', 'month')
        
#         ventes = Vente.objects.filter(DateVente__year=year, DateVente__month=month).annotate(mois=ExtractMonth('DateVente'),annee=ExtractYear('DateVente')).values('mois', 'annee').annotate(chiffre_affaires=Sum('MontantTotal')).order_by('annee', 'mois')
#         years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
#         total_sales = [sale['total_sales'] for sale in sales_by_date]
#         best_employee_sales = format_number(total_sales)

#         # Calculer le chiffre d'affaires total de toutes les ventes
#         total_chiffre_affaires = Vente.objects.filter(DateVente__year=year, DateVente__month=month).aggregate(total_chiffre_affaires=Sum('MontantTotal'))['total_chiffre_affaires']
#         total_chiffre_affaires = format_number(total_chiffre_affaires)
#         labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
#         data = [vente['chiffre_affaires'] for vente in ventes]
#         data = [float(vente['chiffre_affaires']) for vente in ventes]
        
#         Listeventes = Vente.objects.filter(DateVente__year=year, DateVente__month=month).select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
#         nombre_total_ventes = Listeventes.count()
        
#         liste_client = client.objects.all()
#         nombre_total_client = liste_client.count()
#     else:
#         # Si aucune date n'est sélectionnée, afficher toutes les ventes
#         # ventes = Vente.objects.all()

#         # Récupérer l'utilisateur connecté
#         utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

#         # Utiliser la clé étrangère pour récupérer l'administrateur associé
#         administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
#         # Meilleur produit vendu
#         # best_product = Vente.objects.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold').first()
#         top_5_products = Vente.objects.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold')[:5]
#         # Meilleur employé
#         best_employee = Vente.objects.values('IdVendeur__nom', 'IdVendeur__prenoms').annotate(total_sales=Sum('MontantTotal')).order_by('-total_sales').first()
#         # Top 5 des meilleurs clients
#         top_clients = Vente.objects.values('IdClient__nom', 'IdClient__prenoms').annotate(total_purchases=Count('IdClient')).order_by('-total_purchases')[:5]
        
#         # Agrégation pour obtenir le nombre total de ventes par mois/année
#         sales_by_date = Vente.objects.annotate(
#             month=ExtractMonth('DateVente'),
#             year=ExtractYear('DateVente')
#         ).values('year', 'month').annotate(
#             total_sales=Count('id'),
#         ).order_by('year', 'month')
        
#         ventes = Vente.objects.annotate(
#         mois=ExtractMonth('DateVente'),
#         annee=ExtractYear('DateVente')
#         ).values('mois', 'annee').annotate(
#             chiffre_affaires=Sum('MontantTotal')
#         ).order_by('annee', 'mois')
#         years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
#         total_sales = [sale['total_sales'] for sale in sales_by_date]
#         best_employee_sales = format_number(total_sales)
#         # Calculer le chiffre d'affaires total de toutes les ventes
#         total_chiffre_affaires = Vente.objects.aggregate(total_chiffre_affaires=Sum('MontantTotal'))['total_chiffre_affaires']
        
#         total_chiffre_affaires = format_number(total_chiffre_affaires)
        
#         labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
#         data = [vente['chiffre_affaires'] for vente in ventes]
#         data = [float(vente['chiffre_affaires']) for vente in ventes]
        
#         Listeventes = Vente.objects.all().select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
#         nombre_total_ventes = Listeventes.count()
        
#         liste_client = client.objects.all()
#         nombre_total_client = liste_client.count()
  
#     context = {
#         'utilisateur': utilisateur,
#         'administrateur': administrateur,
#         'top_5_products': top_5_products,
#         'best_employee': best_employee,
#         'top_clients': top_clients,
#         'years_months': years_months,
#         'total_sales': total_sales,
#         'ventes':ventes,
#         'labels': labels,
#         'data': data,
#         'date_form':date_form,
#         'nombre_total_ventes': nombre_total_ventes,
#         'nombre_total_client': nombre_total_client,
#         'total_chiffre_affaires':total_chiffre_affaires,
#         'best_employee_sales':best_employee_sales,
#         # 'ventes_for_date':ventes_for_date
#     }
#     return render(request, 'app/admin/visuels.html', context)

# from django.utils import timezone
@login_required(login_url='connexion')
def visuels(request):
    user = request.user
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    administrateur = get_object_or_404(Adminitrateur, IdUtilisateur=utilisateur)
    
    date_form = DateForm(request.GET)
    if date_form.is_valid():
        selected_date_str = date_form.cleaned_data['date_input']
        selected_date = datetime.strptime(selected_date_str, '%m/%Y')
        year = selected_date.year
        month = selected_date.month
        ventes_for_date = Vente.objects.annotate(
            year=ExtractYear('DateVente'),
            month=ExtractMonth('DateVente')
        ).filter(year=year, month=month)
        
        top_5_products = ventes_for_date.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold')[:5]
        best_employee = ventes_for_date.values('IdVendeur__nom', 'IdVendeur__prenoms').annotate(total_sales=Sum('MontantTotal')).order_by('-total_sales').first()
        top_clients = ventes_for_date.values('IdClient__nom', 'IdClient__prenoms').annotate(total_purchases=Count('IdClient')).order_by('-total_purchases')[:5]
        
        sales_by_date = ventes_for_date.annotate(
            month=ExtractMonth('DateVente'),
            year=ExtractYear('DateVente')
        ).values('year', 'month').annotate(
            total_sales=Count('id')
        ).order_by('year', 'month')
        
        ventes = ventes_for_date.annotate(mois=ExtractMonth('DateVente'), annee=ExtractYear('DateVente')).values('mois', 'annee').annotate(chiffre_affaires=Sum('MontantTotal')).order_by('annee', 'mois')
        years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
        total_sales = [sale['total_sales'] for sale in sales_by_date]
        
        total_chiffre_affaires = ventes_for_date.aggregate(total_chiffre_affaires=Sum('MontantTotal'))['total_chiffre_affaires']
        total_chiffre_affaires = format_number(total_chiffre_affaires)
        labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
        data = [float(vente['chiffre_affaires']) for vente in ventes]
        
        Listeventes = ventes_for_date.select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
        nombre_total_ventes = Listeventes.count()
        
        now = timezone.now()
        # total_ventes = Vente.objects.all()
        total_ventes = ventes_for_date.count()
        # Calculer la date et l'heure il y a 24 heures
        twenty_four_hours_ago = now - timedelta(hours=24)

        # Récupérer les ventes réalisées en moins de 24 heures
        ventes_par_jour = Vente.objects.filter(DateVente__gte=twenty_four_hours_ago)
        nombre_ventes_par_jour = ventes_par_jour.count()
        # Calcul du pourcentage de ventes par jour, arrondi à deux chiffres après la virgule
        pourc_ventes_par_jour = round((nombre_ventes_par_jour * 100) / total_ventes, 2)
        
        order_for_date = Order.objects.annotate(
            year=ExtractYear('created_at'),
            month=ExtractMonth('created_at')
        ).filter(year=year, month=month)
        orders = order_for_date.filter()
        orders_count = orders.count()
        orders_count = format_number(orders_count)
        
        liste_client = client.objects.all()
        nombre_total_client = liste_client.count()
    else:
        top_5_products = Vente.objects.values('IdProduit__Nom').annotate(total_sold=Sum('QuantiteVendu')).order_by('-total_sold')[:5]
        best_employee = Vente.objects.values('IdVendeur__nom', 'IdVendeur__prenoms').annotate(total_sales=Sum('MontantTotal')).order_by('-total_sales').first()
        top_clients = Vente.objects.values('IdClient__nom', 'IdClient__prenoms').annotate(total_purchases=Count('IdClient')).order_by('-total_purchases')[:5]
        
        sales_by_date = Vente.objects.annotate(
            month=ExtractMonth('DateVente'),
            year=ExtractYear('DateVente')
        ).values('year', 'month').annotate(
            total_sales=Count('id')
        ).order_by('year', 'month')
        
        ventes = Vente.objects.annotate(
            mois=ExtractMonth('DateVente'),
            annee=ExtractYear('DateVente')
        ).values('mois', 'annee').annotate(
            chiffre_affaires=Sum('MontantTotal')
        ).order_by('annee', 'mois')
        years_months = [f"{sale['year']}-{sale['month']}" for sale in sales_by_date]
        total_sales = [sale['total_sales'] for sale in sales_by_date]

        total_chiffre_affaires = Vente.objects.aggregate(total_chiffre_affaires=Sum('MontantTotal'))['total_chiffre_affaires']
        total_chiffre_affaires = format_number(total_chiffre_affaires)
        
        labels = [f"{vente['mois']}/{vente['annee']}" for vente in ventes]
        data = [float(vente['chiffre_affaires']) for vente in ventes]
        
        # order_for_date = Order.objects.annotate(
        #     year=ExtractYear('created_at'),
        #     month=ExtractMonth('created_at')
        # ).filter(year=year, month=month)
        orders = Order.objects.filter(is_ordered=True)
        orders_count = orders.count()
        orders_count = format_number(orders_count)
        
        Listeventes = Vente.objects.all().select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur')
        nombre_total_ventes = Listeventes.count()
        
        now = timezone.now()
        # Calculer la date et l'heure il y a 24 heures
        twenty_four_hours_ago = now - timedelta(hours=24)

        # Récupérer les ventes réalisées en moins de 24 heures
        ventes_par_jour = Vente.objects.filter(DateVente__gte=twenty_four_hours_ago)
        nombre_ventes_par_jour = ventes_par_jour.count()
        # Calcul du pourcentage de ventes par jour, arrondi à deux chiffres après la virgule
        pourc_ventes_par_jour = round((nombre_ventes_par_jour * 100) / nombre_total_ventes, 2)
        
        liste_client = client.objects.all()
        nombre_total_client = liste_client.count()
  
    context = {
        'pourc_ventes_par_jour':pourc_ventes_par_jour,
        'utilisateur': utilisateur,
        'administrateur': administrateur,
        'top_5_products': top_5_products,
        'best_employee': best_employee,
        'top_clients': top_clients,
        'years_months': years_months,
        'total_sales': total_sales,
        'ventes': ventes,
        'labels': labels,
        'orders_count':orders_count,
        'data': data,
        'date_form': date_form,
        'nombre_total_ventes': nombre_total_ventes,
        'nombre_total_client': nombre_total_client,
        'total_chiffre_affaires': total_chiffre_affaires,
        'best_employee_sales': format_number(best_employee['total_sales'] if best_employee else 0),
    }
    return render(request, 'app/admin/visuels.html', context)

@login_required(login_url='connexion')
def calendier_admin(request):
    return render(request, 'app/admin/calendier.html')

@login_required(login_url='connexion')
def calendier_vendeur(request):
    return render(request, 'app/Vendeur/calendier.html')

@login_required(login_url='connexion')
def calendier_gestionnaireStock(request):
    return render(request, 'app/GestionnaireStock/calendier.html')

# utilisateur, _ = Utilisateur.objects.get_or_create(username=row['Type'])
# def handle_uploaded_file(file, user_id):
#     # IdVendeur=request.user.id
#     if file.name.endswith('.csv'):
#         data = pd.read_csv(file, sep=";")
#     elif file.name.endswith('.xlsx'):
#         data = pd.read_excel(file)
#     else:
#         raise ValueError("Le fichier n'est pas un format supporté. Seuls CSV et Excel sont acceptés.")
    
#     df=data.copy()   
#     for index, row in df.iterrows():
#         # Split le nom pour obtenir prenoms et nom
#         name_parts = row['Name'].split(' ', 1)
#         prenoms = name_parts[0]
#         nom = name_parts[1] if len(name_parts) > 1 else ''  # Gère les noms sans prénom
        
#         # Créer ou récupérer le client
#         client_instance, created = client.objects.get_or_create(
#             prenoms=prenoms, 
#             nom=nom, 
#             defaults={'genre': row['Gender']}
#         )
        
#         vendeur_instance = Vendeur.objects.get(id=user_id)
#         # Créer ou récupérer la catégorie de produit
#         categorie, _ = CategorieProduit.objects.get_or_create(nom=row['Type'])
        
#         # Créer ou récupérer le produit
#         produit, created_produit = Produit.objects.get_or_create(
#             Nom=row['Produit'],
#             PrixUnitaire=row['Prix'],
#             IdCategorie=categorie
#         )
#         stock, created_stock = Stock.objects.get_or_create(
#             IdProduit=produit,
#             QuantiteStock=250,
#         )
        
#          # Créer la vente si le produit, le client et la catégorie n'existent pas déjà
        
#         Vente.objects.create(
#             IdVendeur=vendeur_instance,  # Vous devez définir l'ID du vendeur approprié
#             IdClient=client_instance,
#             IdProduit=produit,
#             QuantiteVendu=1,  # Vous devez définir la quantité vendue appropriée
#             MontantTotal=row['Prix'],
#             DateVente=row['Date']
#         )

from django.utils.crypto import get_random_string

from django.utils.text import slugify
def handle_uploaded_file(file, user_id):
    if file.name.endswith('.csv'):
        data = pd.read_csv(file, sep=";")
    elif file.name.endswith('.xlsx'):
        data = pd.read_excel(file)
    else:
        raise ValueError("Le fichier n'est pas un format supporté. Seuls CSV et Excel sont acceptés.")
    
    df = data.copy()

    for index, row in df.iterrows():
        # Split le nom pour obtenir prenoms et nom
        name_parts = row['Name'].split(' ', 1)
        prenoms = name_parts[0]
        nom = name_parts[1] if len(name_parts) > 1 else ''  # Gère les noms sans prénom

        # Extraire l'année de la colonne Date
        annee = pd.to_datetime(row['Date']).year
        # Générer email et username
        email = f"{prenoms}.{nom}2024@gmail.com".lower()
        username = f"{prenoms}.{nom}2024".lower()
        
        # Définir le rôle par défaut et le mot de passe par défaut
        roles = 'Client'
        password = '123456789'
        
        # Créer ou récupérer l'utilisateur
        utilisateur, created = Utilisateur.objects.get_or_create(
            email=email,
            defaults={
                'username': username,
                'roles': roles,
                'is_active': True,
            }
        )
        
        if created:
            # Si l'utilisateur est créé, définir le mot de passe
            utilisateur.set_password(password)
            utilisateur.save()

        # Créer ou récupérer le client
        client_instance, created = client.objects.get_or_create(
            prenoms=prenoms,
            nom=nom,
            defaults={'genre': row['Gender'], 'ville': row.get('City', ''), 'telephone': row.get('Phone', 1234567890), 'IdUtilisateur': utilisateur}
        )

        try:
            vendeur_instance = Vendeur.objects.get(id=user_id)
        except Vendeur.DoesNotExist:
            raise ValueError("Le vendeur avec l'ID spécifié n'existe pas.")

        # Créer ou récupérer la catégorie de produit
         # Créer ou récupérer la catégorie de produit, avec le slug basé sur le nom sans espace
        nom_categorie = row['Type']
        slug_categorie = slugify(nom_categorie.replace(" ", ""))
        categorie, _ = CategorieProduit.objects.get_or_create(
            nom=nom_categorie,
            defaults={'slug': slug_categorie}
        )
        
        # Générer le slug du produit
        
        description = 'Lorem ipsum dolor sit amet consectetur adipisicing elit. A labore cum quisquam rerum possimus ipsam tenetur eum exercitationem eveniet laborum at minus suscipit doloremque dolorem error, perspiciatis rem, atque laudantium?'
        nom_produit = row['Produit']
        slug_produit = slugify(nom_produit.replace(" ", ""))

        # Créer ou récupérer le produit
        produit, created_produit = Produit.objects.get_or_create(
            Nom=nom_produit,
            defaults={
                'PrixUnitaire': row['Prix'],
                'slug': slug_produit,
                'description':description,
                'IdCategorie': categorie
            }
        )
        
        

        # Créer ou récupérer le stock
        stock, created_stock = Stock.objects.get_or_create(
            IdProduit=produit,
            defaults={'QuantiteStock': 250}
        )

        # Créer la vente
        Vente.objects.create(
            IdVendeur=vendeur_instance,
            IdClient=client_instance,
            IdProduit=produit,
            QuantiteVendu=1,
            MontantTotal=row['Prix'],
            DateVente=row['Date']
        )
@login_required(login_url='connexion')
def ventes(request):
    user = request.user.id
     # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user)
    # form = UploadFileForm(request.POST, request.FILES)
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            if file.name.endswith('.csv'):
                # Traitement du fichier CSV avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/Vendeur/ventes.html', {'form': form})

            elif file.name.endswith(('.xlsx', '.xls')):
                # Traitement du fichier Excel avec Pandas
                handle_uploaded_file(file, vendeur.id)
                messages.success(request, "Vente enregistrée avec succès.")
                return render(request, 'app/Vendeur/ventes.html', {'form': form})

            else:
                messages.warning(request, 'Le fichier doit être au format CSV ou excel')
    else:
        form = UploadFileForm()
    # Filtrer les ventes en fonction du vendeur
    ventes = Vente.objects.filter(IdVendeur=vendeur.id).select_related('IdClient', 'IdProduit', 'IdProduit__IdCategorie', 'IdVendeur').order_by('-DateVente')
    nombre_total_ventes = ventes.count()
    paginator = Paginator(ventes, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    ventes = paginator.get_page(page_number)
    return render(request, 'app/Vendeur/ventes.html',locals())


# def get_client_details(request, client_id):
#     try:
#         client_obj = client.objects.get(pk=client_id)
#         data = {
#             'nom': client_obj.nom,
#             'prenoms': client_obj.prenoms,
#             'genre': client_obj.genre,
#         }
#         return JsonResponse(data)
#     except client.DoesNotExist:
#         return JsonResponse({'error': 'Client Non Trouver'}, status=404)

def get_client_details(request, client_id):
    try:
        client_obj = client.objects.get(pk=client_id)
        data = {
            'nom': client_obj.nom,
            'prenoms': client_obj.prenoms,
            'genre': client_obj.genre,
        }
        return JsonResponse(data)
    except client.DoesNotExist:
        return JsonResponse({'error': 'Client Non Trouver'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

ProduitFormSet = inlineformset_factory(client, Vente, form=VenteForm, extra=1)
def ajout_vente(request):
    user = request.user.id
     # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user) 
    if request.method == 'POST':
        client_form = ClientForm(request.POST)
        
        if client_form.is_valid():
            # Vérifier si le client existe déjà
            nom = client_form.cleaned_data['nom']
            prenoms = client_form.cleaned_data['prenoms']
            genre = client_form.cleaned_data['genre']
            
            existing_client = client.objects.filter(nom=nom, prenoms=prenoms, genre=genre).first()
            
            if existing_client:
                new_client = existing_client
            else:
                new_client = client_form.save()
            
            id_user = request.user.id
            vendeur = get_object_or_404(Vendeur, IdUtilisateur=id_user)
            produit_formset = ProduitFormSet(request.POST, instance=new_client)
            if produit_formset.is_valid():
                instances = produit_formset.save(commit=False)
                error_flag = False
                
                for instance in instances:
                    produit = instance.IdProduit
                    instance.MontantTotal = produit.PrixUnitaire * instance.QuantiteVendu
                    # date_et_heure = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    # instance.DateVente = timezone.now
                    instance.IdVendeur_id = vendeur.id

                    # Vérification de la quantité en stock
                    produit_stock, _ = Stock.objects.get_or_create(IdProduit=produit)
                    if produit_stock.QuantiteStock < instance.QuantiteVendu:
                        messages.warning(request, f"La quantité en stock ({produit_stock.QuantiteStock}) est insuffisante pour la vente.")
                        error_flag = True
                        continue

                    # Vérifiez si la soustraction ne résulte pas en un nombre négatif
                    if produit_stock.QuantiteStock - instance.QuantiteVendu < 0:
                        messages.warning(request, "La quantité en stock ne peut pas être négative après la vente.")
                        error_flag = True
                        continue

                    instance.save()

                if not error_flag:
                    return redirect('recu_vente', client_id=new_client.id)

    else:
        client_form = ClientForm()
        produit_formset = ProduitFormSet()

    return render(request, 'app/Vendeur/ajout_vente.html', locals())

def recu_vente(request, client_id):
    user = request.user.id
     # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user) 
    clients = get_object_or_404(client, id=client_id)
    # Création de l'objet datetime pour la date et l'heure actuelles
    date_et_heure = datetime.now()  # Format jour/mois/année heure:minute:seconde
    ventes = Vente.objects.filter(IdClient=clients, DateVente__date=date_et_heure.date(), DateVente__time__hour=date_et_heure.hour, DateVente__time__minute=date_et_heure.minute)
    total_vente = sum(vente.MontantTotal for vente in ventes)
    # Créer une instance Recu après avoir enregistré les ventes
    recu = Recu.objects.create()
    for vente in ventes:
        vente.DateVente = date_et_heure
        vente.save()
        
        # Associer la vente au recu
        recu.IdVente.add(vente)
    
    return render(request, 'app/Vendeur/recu.html', locals())

def list_recu(request):
    user = request.user.id
     # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user) 
    # recu_instance = Recu.objects.all()
    # Récupère tous les reçus et filtre ceux ayant au moins une vente associée
    recu_instance = Recu.objects.annotate(vente_count=Count('IdVente')).filter(vente_count__gt=0)
    paginator = Paginator(recu_instance, 10)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    recu_instance = paginator.get_page(page_number)
    return render(request, 'app/Vendeur/list_recu.html', {'recu_instance': recu_instance, 'utilisateur':utilisateur, 'vendeur': vendeur})
    
def list_commande(request):
    # user = request.user.id
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    # Utiliser la clé étrangère pour récupérer l'administrateur associé
    
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
    # clients = get_object_or_404(client, IdUtilisateur=utilisateur)
    orders = Order.objects.order_by('-created_at').filter(is_ordered=True)
    
    nombre_total_commande = orders.count()
    paginator = Paginator(orders, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        # 'clients': clients,
        'utilisateur': utilisateur,
        'nombre_total_commande': nombre_total_commande,
        'vendeur': vendeur
    }
    return render(request, 'app/Vendeur/list_commande.html', context)


# @login_required(login_url='connexion')
# def valider_commande(request, order_id):
#     # Récupérer l'utilisateur connecté
#     utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#     # Utiliser la clé étrangère pour récupérer l'administrateur associé
#     vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
#     # clients = get_object_or_404(client, IdUtilisateur=utilisateur)
#     # order_id = request.GET.get('order_id')
#     order = Order.objects.get(order_number=order_id)
#     order.is_ordered = True
#     order.save()
#     return redirect('list_commande')
    
# @login_required(login_url='connexion')
# def detail_commande(request, order_id):
#     # Récupérer l'utilisateur connecté
#     utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#     # Utiliser la clé étrangère pour récupérer l'administrateur associé
#     vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
#     # clients = get_object_or_404(client, IdUtilisateur=utilisateur)
#     orders_detail = OrderProduct.objects.filter(order__order_number=order_id)
#     order = Order.objects.get(order_number=order_id)
#     subTotal = 0
#     for i in orders_detail:
#         subTotal += i.product_price * i.quantity 
    
#     for item in orders_detail:
#         total_price = item.product_price * item.quantity
#     context = {
#         'orders_detail': orders_detail,
#         'order': order,
#         'subTotal': subTotal,
#         # 'clients': clients
#         'vendeur': vendeur,
#         'utilisateur': utilisateur,
#     }
#     return render(request, 'app/Vendeur/detail_commande.html', context)


#     # user = request.user.id
#     #  # Récupérer l'utilisateur connecté
#     # utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
#     # vendeur = get_object_or_404(Vendeur, IdUtilisateur=user)
#     # # commande_instance = Commande.objects.all()
#     # # Récupère tous les commandes et filtre ceux ayant au moins une vente associée
#     # commande_instance = Commande.objects.annotate(vente_count=Count('IdVente')).filter(vente_count__gt=0)
#     # paginator = Paginator(commande_instance, 10)  # Affiche 25 commandes par page


@login_required(login_url='connexion')
def detail_commande(request, order_id):
    # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)
    vendeur = get_object_or_404(Vendeur, IdUtilisateur=utilisateur)
    orders_detail = OrderProduct.objects.filter(order__order_number=order_id)
    order = get_object_or_404(Order, order_number=order_id)
    subTotal = 0
    for i in orders_detail:
        subTotal += i.product_price * i.quantity 
    
    for item in orders_detail:
        item.total_prices = item.product_price * item.quantity

    if request.method == 'POST':
        # Récupérer les données du formulaire
        order_id = request.POST.get('order_id')
        user_id = request.POST.get('user')
        status = request.POST.get('status')
        product_ids = request.POST.getlist('products')
        quantities = request.POST.getlist('quantities')
        prices = request.POST.getlist('prices')
        total_prices = request.POST.getlist('total_prices')
        
        print('client', user_id)
        print('product', product_ids)
        print('quantities', quantities)
        print('prices', prices)
        print('total_prices', total_prices)

        # Récupérer le client
        client_instance = get_object_or_404(client, id=user_id)

        # Enregistrer les ventes
        for i in range(len(product_ids)):
            product_id = product_ids[i]
            quantity = quantities[i]
            price = prices[i]
            total_price = total_prices[i]

            # Récupérer le produit
            product_instance = get_object_or_404(Produit, id=product_id)
            
            quantite = int(quantity)
            # Créer la vente
            vente = Vente.objects.create(
                IdVendeur=vendeur,
                IdClient=client_instance,
                IdProduit=product_instance,
                QuantiteVendu=quantite,
                MontantTotal=total_price
            )
            vente.save()

        # Mettre à jour le statut de la commande
        order.status = status
        order.save()

        messages.success(request, 'La commande a été mise à jour et les ventes ont été enregistrées avec succès.')
        return redirect('list_commande')  # Redirigez vers une page de succès appropriée
    status_code = 'En attente'
    orders_status = Order.objects.filter(status=status_code)
    orders_status_count = orders_status.count()
    print(orders_status_count)
    context = {
        'orders_detail': orders_detail,
        'order': order,
        'subTotal': subTotal,
        'vendeur': vendeur,
        'utilisateur': utilisateur,
        'orders_status_count': orders_status_count,
    }
    return render(request, 'app/Vendeur/detail_commande.html', context)
    
    
    
 
def details_vente(request, recu_id):
    # recu_instance = Recu.objects.get(id=id)
    # ventes_associees = recu_instance.IdVente.all()
    user = request.user.id
     # Récupérer l'utilisateur connecté
    utilisateur = get_object_or_404(Utilisateur, id=request.user.id)

    vendeur = get_object_or_404(Vendeur, IdUtilisateur=user) 
    recu_instance = get_object_or_404(Recu, id=recu_id)
    ventes_associees = recu_instance.IdVente.all()
    total_vente = sum(vente.MontantTotal for vente in ventes_associees)
    # Le reste de votre code...
    return render(request, 'app/Vendeur/details_vente.html', {'recu': recu_instance, 'ventes': ventes_associees, 'total_vente':total_vente, 'utilisateur':utilisateur, 'vendeur': vendeur})
    
def supprimer_vente(request, vente_id):
    vente = Vente.objects.get(id=vente_id)
    vente.delete()
    messages.success(request, 'La vente a été supprimée avec succès.')
    return redirect('ventes')

def get_product_details(request, product_id):
    try:
        product = Produit.objects.get(id=product_id)
        stock, _ = Stock.objects.get_or_create(IdProduit=product)
        
        data = {
            'id': product.id,
            'nom': product.Nom,
            'category': product.IdCategorie.nom,
            'price': product.PrixUnitaire,
            'stock': stock.QuantiteStock
        }
        
        return JsonResponse(data)
    
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit non trouvé'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def liste_stock(request):
    stocks = Stock.objects.all().select_related('IdProduit', 'IdProduit__IdCategorie').order_by('QuantiteStock')
    notifications = Notification.objects.filter(est_lu=False)
    paginator = Paginator(stocks, 25)  # Affiche 25 ventes par page

    page_number = request.GET.get('page')
    stocks = paginator.get_page(page_number)
    return render(request, 'app/GestionnaireStock/liste_stock.html', {'stocks': stocks, 'notifications':notifications})



@require_POST
def mark_notification_as_read(request, notification_id):
    if request.headers.get('X-Requested-With') != 'XMLHttpRequest':
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    notification = get_object_or_404(Notification, id=notification_id)  # Assurez-vous que la notification appartient à l'utilisateur
    notification.est_lu = True
    notification.save()
    
    return JsonResponse({'success': True})

def modif_stock(request):
    if request.method == 'POST':
        form_data = request.POST
        produit_keys = [key for key in form_data.keys() if key.startswith('produit_')]
        
        for key in produit_keys:
            produit_id = form_data[key]
            quantite_key = key.replace('produit_', 'quantite_')
            quantite = form_data[quantite_key]
            
            if produit_id and quantite:
                produit = Produit.objects.get(pk=produit_id)
                try:
                    stock = Stock.objects.get(IdProduit=produit)
                    nouvelle_quantite = stock.QuantiteStock + int(quantite)  # Addition de l'ancienne et de la nouvelle quantité
                    stock.QuantiteStock = nouvelle_quantite
                    stock.Date = timezone.now()
                    stock.save()
                except Stock.DoesNotExist:
                    Stock.objects.create(
                        IdProduit=produit,
                        QuantiteStock=quantite,
                        Date=timezone.now()
                    )
                    
        messages.success(request, f"Stock mise à jour avec succès.")
        return redirect('liste_stock')
    else:
        form = StockUpdateForm()
    return render(request, 'app/GestionnaireStock/modif_stock.html', {'form': form})

def get_quantite(request, produitId):
    try:
        produit = Stock.objects.get(pk=produitId)
        quantite = produit.QuantiteStock
        return JsonResponse({'quantite': quantite})
    except Produit.DoesNotExist:
        return JsonResponse({'error': 'Produit not found'}, status=404)
    
# def get_all_products(request):
#     products = Produit.objects.all().values('id', 'Nom')
#     return JsonResponse(list(products), safe=False)